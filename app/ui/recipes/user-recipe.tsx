'use client';

import { Cookbook, IngredientList, Recipe, UserRecipe } from '@/app/lib/definitions';
import { UpdateRecipe, DeleteRecipe } from '@/app/ui/recipes/buttons';


export default function ViewRecipeWithUserRecipe({
  recipe,
  cookbooks_map,
  user_recipe,
}: {
  recipe: Recipe;
  cookbooks_map: { [key: string]: Cookbook };
  user_recipe: UserRecipe;
}) {
  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-4xl font-bold mb-2">{recipe.name_of_dish}</h1>
      <div className="flex w-full items-center justify-between pt-4 mb-4">
        <div className="flex justify-end gap-2">
          <UpdateRecipe id={recipe._id} />
          <DeleteRecipe id={recipe._id} />
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <p>
          <span className="font-semibold">Serving Size:</span> {recipe.serving_size}
        </p>
        <p>
          <span className="font-semibold">Page Number:</span> {recipe.page_number}
        </p>
        <p>
          <span className="font-semibold">Cookbook:</span> {cookbooks_map[recipe.cookbook_key].name}
        </p>
        <p>
          <span className="font-semibold">Status:</span> {user_recipe.status}
        </p>
        <p>
          <span className="font-semibold">Rating:</span> {user_recipe.rating}
        </p>
        <p>
          <span className="font-semibold">Your Note:</span> {user_recipe.note}
        </p>
      </div>

      <h2 className="text-2xl font-semibold mb-2">Ingredients</h2>
      <div className="mb-6">
        {(Object.entries(recipe.ingredients) as [keyof IngredientList, string[]][]).map(
          ([category, items]) => items.length > 0 ? (
            <div key={category} className="mb-4">
              <h3 className="text-xl font-semibold mb-1">
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </h3>
              <ul className="list-disc list-inside ml-4">
                {items.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null
        )}
      </div>

      <h2 className="text-2xl font-semibold mb-4">Instructions</h2>
      <div className="mb-6">
        {recipe.instructions.map((instruction, index) => (
          <div key={index} className="bg-white p-6 rounded-lg shadow mb-4">
            <h3 className="text-lg font-semibold mb-2">
              Step {index + 1}:
            </h3>
            <ul className="list-decimal list-inside ml-4 text-gray-700">
              {instruction.details.map((detail, idx) => (
                <li key={idx} className="mb-1">{detail}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {recipe.note && (
        <>
          <h2 className="text-2xl font-semibold mb-2">Note</h2>
          <p className="mb-6">{recipe.note}</p>
        </>
      )}
    </div>
  );
}

