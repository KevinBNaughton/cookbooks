import {
  UpdateRecipe,
  DeleteRecipe,
  ViewRecipe,
} from "@/app/ui/recipes/buttons";
import { fetchFilteredRecipes } from "@/app/lib/data";
import { Recipe } from "@/app/lib/definitions";
import RecipeStatus from "./status";
import { APIAuthError } from "@/app/lib/errors";

export default async function RecipesTable({
  query,
  currentPage,
  status,
}: {
  query: string;
  currentPage: number;
  status: "" | "cooked!" | "uncooked";
}) {
  let recipes: Recipe[] = [];
  try {
    recipes = await fetchFilteredRecipes(query, status, currentPage);
  } catch (error) {
    if (error instanceof APIAuthError) {
      console.error("You should log out");
      // TODO - make this work?
      // await signOut();
    }
  }

  return (
    <div className="mt-6 flow-root">
      <div className="inline-block min-w-full align-middle">
        <div className="rounded-lg bg-gray-50 p-2 md:pt-0">
          <div className="md:hidden">
            {recipes?.map((recipe) => (
              <div
                key={recipe._id}
                className="mb-2 w-full rounded-md bg-white p-4"
              >
                <div className="flex flex-col items-center justify-between border-b pb-4">
                  <div className="w-full">
                    <div className="mb-2 justify-center items-center">
                      <p>{recipe.name_of_dish}</p>
                    </div>
                    <p className="text-sm text-gray-500">
                      Page Number: {recipe.page_number}
                    </p>
                  </div>
                </div>
                <div className="flex w-full items-center justify-between pt-4">
                  <RecipeStatus
                    status={recipe.user_recipe?.status || "uncooked"}
                  />
                  <div className="flex justify-end gap-2">
                    <ViewRecipe id={recipe._id} />
                    <UpdateRecipe id={recipe._id} />
                    <DeleteRecipe id={recipe._id} />
                  </div>
                </div>
              </div>
            ))}
          </div>
          <table className="hidden min-w-full text-gray-900 md:table">
            <thead className="rounded-lg text-left text-sm font-normal">
              <tr>
                <th scope="col" className="px-4 py-5 font-medium sm:pl-6">
                  Recipe
                </th>
                <th scope="col" className="px-3 py-5 font-medium">
                  Cookbook
                </th>
                <th scope="col" className="px-3 py-5 font-medium">
                  Status
                </th>
                <th scope="col" className="relative py-3 pl-6 pr-3">
                  <span className="sr-only">Edit</span>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white">
              {recipes?.map((recipe) => (
                <tr
                  key={recipe._id}
                  className="w-full border-b py-3 text-sm last-of-type:border-none [&:first-child>td:first-child]:rounded-tl-lg [&:first-child>td:last-child]:rounded-tr-lg [&:last-child>td:first-child]:rounded-bl-lg [&:last-child>td:last-child]:rounded-br-lg"
                >
                  <td className="whitespace-nowrap py-3 pl-6 pr-3">
                    <div className="flex items-center gap-3">
                      <p>{recipe.name_of_dish}</p>
                    </div>
                  </td>
                  <td className="whitespace-nowrap px-3 py-3">
                    {recipe.page_number}
                  </td>
                  <td className="whitespace-nowrap px-3 py-3">
                    <RecipeStatus status={"uncooked"} />
                  </td>
                  <td className="whitespace-nowrap py-3 pl-6 pr-3">
                    <div className="flex justify-end gap-3">
                      <ViewRecipe id={recipe._id} />
                      <UpdateRecipe id={recipe._id} />
                      <DeleteRecipe id={recipe._id} />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
