import Pagination from "@/app/ui/recipes/pagination";
import Search from "@/app/ui/search";
import RecipesTable from "@/app/ui/recipes/table";
import { lusitana } from "@/app/ui/fonts";
import { RecipesTableSkeleton } from "@/app/ui/skeletons";
import { Suspense } from "react";
import { fetchCookbooksAsMap, fetchRecipesPages } from "@/app/lib/data";
import SearchStatus from "@/app/ui/search-status";

export default async function Page(props: {
  searchParams?: Promise<{
    query?: string;
    page?: string;
    status?: "" | "uncooked" | "cooked!";
  }>;
}) {
  const searchParams = await props.searchParams;
  const query = searchParams?.query || "";
  const status = searchParams?.status || "";
  const currentPage = Number(searchParams?.page) || 1;
  const [totalPages, cookbooks_map] = await Promise.all([
    fetchRecipesPages(query),
    fetchCookbooksAsMap(),
  ]);

  return (
    <div className="w-full">
      <div className="flex w-full items-center justify-between">
        <h1 className={`${lusitana.className} text-2xl`}>Recipes</h1>
      </div>
      <div className="mt-4 flex-col items-center justify-between gap-2 md:hidden">
        <Search placeholder="Search recipes..." />
        <div className="mb-2" />
        <SearchStatus status={status} />
      </div>
      <div className="hidden mt-4 flex items-center justify-between gap-2 md:flex">
        <Search placeholder="Search recipes..." />
        <SearchStatus status={status} />
        {/*<CreateRecipe />*/}
      </div>
      <Suspense
        key={query + currentPage + status}
        fallback={<RecipesTableSkeleton />}
      >
        <RecipesTable
          query={query}
          currentPage={currentPage}
          status={status}
          cookbooks_map={cookbooks_map}
        />
      </Suspense>
      <div className="mt-5 flex w-full justify-center">
        <Pagination totalPages={totalPages} />
      </div>
    </div>
  );
}
