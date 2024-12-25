import Breadcrumbs from "@/app/ui/recipes/breadcrumbs";
import {
  fetchCookbooksAsMap,
  fetchRecipeById,
  fetchUserRecipeById,
} from "@/app/lib/data";
import UserRecipeView from "@/app/ui/recipes/user-recipe";
import { notFound } from "next/navigation";

export default async function Page(props: { params: Promise<{ id: string }> }) {
  const params = await props.params;
  const id = params.id;
  const [recipe, cookbooks_map, user_recipe] = await Promise.all([
    fetchRecipeById(id),
    fetchCookbooksAsMap(),
    fetchUserRecipeById(id),
  ]);
  if (!recipe || !user_recipe) {
    notFound();
  }

  return (
    <main>
      <Breadcrumbs
        breadcrumbs={[
          { label: "Recipes", href: "/dashboard/recipes" },
          {
            label: "View Recipe",
            href: `/dashboard/recipes/${id}/view`,
            active: true,
          },
        ]}
      />
      <UserRecipeView
        recipe={recipe}
        cookbooks_map={cookbooks_map}
        user_recipe={user_recipe}
      />
    </main>
  );
}
