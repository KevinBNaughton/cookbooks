'use client';

import { Cookbook, Recipe, UserRecipe } from '@/app/lib/definitions';
import {
  CheckIcon,
  ClockIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline';
import Link from 'next/link';
import { Button } from '@/app/ui/button';
import { updateUserRecipe, State } from '@/app/lib/actions';
import { useActionState } from 'react';


export default function EditRecipeForm({
  recipe,
  cookbooks,
  user_recipe,
}: {
  recipe: Recipe;
  cookbooks: Cookbook[];
  user_recipe: UserRecipe;
}) {
  const initialState: State = { message: null, errors: {} };
  const updateUserRecipeWithId = updateUserRecipe.bind(null, recipe);
  const [_state, formAction] = useActionState(updateUserRecipeWithId, initialState);

  return (
    <form action={formAction}>
      <div className="rounded-md bg-gray-50 p-4 md:p-6">
        {/* Cookbook Name */}
        <div className="mb-4">
          <label htmlFor="cookbook" className="mb-2 block text-sm font-medium">
            Choose Cookbook
          </label>
          <div className="relative">
            <select
              id="cookbook"
              name="CookbookId"
              className="peer block w-full cursor-pointer rounded-md border border-gray-200 py-2 pl-10 text-sm outline-2 placeholder:text-gray-500"
              defaultValue={recipe.cookbook_key}
            >
              <option value="" disabled>
                Select a cookbook
              </option>
              {cookbooks.map((cookbook) => (
                <option key={cookbook.key} value={cookbook.key}>
                  {cookbook.name}
                </option>
              ))}
            </select>
            <UserCircleIcon className="pointer-events-none absolute left-3 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-gray-500" />
          </div>
        </div>

        {/* Recipe Status */}
        <fieldset>
          <legend className="mb-2 block text-sm font-medium">
            Set the recipe status
          </legend>
          <div className="rounded-md border border-gray-200 bg-white px-[14px] py-3">
            <div className="flex gap-4">
              <div className="flex items-center">
                <input
                  id="uncooked"
                  name="status"
                  type="radio"
                  value="uncooked"
                  defaultChecked={user_recipe.status === 'uncooked'}
                  className="h-4 w-4 cursor-pointer border-gray-300 bg-gray-100 text-gray-600 focus:ring-2"
                />
                <label
                  htmlFor="uncooked"
                  className="ml-2 flex cursor-pointer items-center gap-1.5 rounded-full bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-600"
                >
                  Uncooked <ClockIcon className="h-4 w-4" />
                </label>
              </div>
              <div className="flex items-center">
                <input
                  id="cooked!"
                  name="status"
                  type="radio"
                  value="cooked!"
                  defaultChecked={user_recipe.status === 'cooked!'}
                  className="h-4 w-4 cursor-pointer border-gray-300 bg-gray-100 text-gray-600 focus:ring-2"
                />
                <label
                  htmlFor="cooked!"
                  className="ml-2 flex cursor-pointer items-center gap-1.5 rounded-full bg-green-500 px-3 py-1.5 text-xs font-medium text-white"
                >
                  Cooked! <CheckIcon className="h-4 w-4" />
                </label>
              </div>
            </div>
          </div>
        </fieldset>
      </div>
      <div className="mt-6 flex justify-end gap-4">
        <Link
          href="/dashboard/recipes"
          className="flex h-10 items-center rounded-lg bg-gray-100 px-4 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-200"
        >
          Cancel
        </Link>
        <Button type="submit">Edit Recipe</Button>
      </div>
    </form>
  );
}
