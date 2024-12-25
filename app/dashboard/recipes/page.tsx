import Pagination from "@/app/ui/recipes/pagination";
import Search from "@/app/ui/search";
import Table from "@/app/ui/recipes/table";
import { lusitana } from "@/app/ui/fonts";
import { RecipesTableSkeleton } from "@/app/ui/skeletons";
import { Suspense } from "react";
import { fetchRecipesPages } from "@/app/lib/data";
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
  const totalPages = await fetchRecipesPages(query);

  return (
    <div className="w-full">
      <div className="flex w-full items-center justify-between">
        <h1 className={`${lusitana.className} text-2xl`}>Recipes</h1>
      </div>
      <div className="mt-4 flex items-center justify-between gap-2 md:mt-8">
        <Search placeholder="Search recipes..." />
        <SearchStatus status={status} />
        {/*<CreateRecipe />*/}
      </div>
      <Suspense
        key={query + currentPage + status}
        fallback={<RecipesTableSkeleton />}
      >
        <Table query={query} currentPage={currentPage} status={status} />
      </Suspense>
      <div className="mt-5 flex w-full justify-center">
        <Pagination totalPages={totalPages} />
      </div>
    </div>
  );
}
