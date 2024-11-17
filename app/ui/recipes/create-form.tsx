import Link from 'next/link';
import {
  CheckIcon,
  ClockIcon,
  CurrencyDollarIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline';
import { Button } from '@/app/ui/button';
import { Cookbook } from '@/app/lib/definitions';

export default function Form({ cookbooks }: { cookbooks: Cookbook[] }) {
  return (
    <form>
      <div className="rounded-md bg-gray-50 p-4 md:p-6">
        {/* Cookbook Name */}
        <div className="mb-4">
          <label htmlFor="cookbook" className="mb-2 block text-sm font-medium">
            Choose cookbook
          </label>
          <div className="relative">
            <select
              id="cookbook"
              name="cookbookId"
              className="peer block w-full cursor-pointer rounded-md border border-gray-200 py-2 pl-10 text-sm outline-2 placeholder:text-gray-500"
              defaultValue=""
            >
              <option value="" disabled>
                Select a Cookbook
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

        {/* User Recipe Rating */}
        <div className="mb-4">
          <label htmlFor="rating" className="mb-2 block text-sm font-medium">
            Give a rating
          </label>
          <div className="relative mt-2 rounded-md">
            <div className="relative">
              <input
                id="rating"
                name="rating"
                type="number"
                step="1"
                placeholder="Enter Rating 1-10"
                className="peer block w-full rounded-md border border-gray-200 py-2 pl-10 text-sm outline-2 placeholder:text-gray-500"
              />
              <CurrencyDollarIcon className="pointer-events-none absolute left-3 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-gray-500 peer-focus:text-gray-900" />
            </div>
          </div>
        </div>

        {/* User Recipe Status */}
        <fieldset>
          <legend className="mb-2 block text-sm font-medium">
            Set the status
          </legend>
          <div className="rounded-md border border-gray-200 bg-white px-[14px] py-3">
            <div className="flex gap-4">
              <div className="flex items-center">
                <input
                  id="uncooked"
                  name="status"
                  type="radio"
                  value="uncooked"
                  className="h-4 w-4 cursor-pointer border-gray-300 bg-gray-100 text-gray-600 focus:ring-2"
                />
                <label
                  htmlFor="uncooked"
                  className="ml-2 flex cursor-pointer items-center gap-1.5 rounded-full bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-600"
                >
                  uncooked <ClockIcon className="h-4 w-4" />
                </label>
              </div>
              <div className="flex items-center">
                <input
                  id="cooked!"
                  name="status"
                  type="radio"
                  value="cooked!"
                  className="h-4 w-4 cursor-pointer border-gray-300 bg-gray-100 text-gray-600 focus:ring-2"
                />
                <label
                  htmlFor="cooked!"
                  className="ml-2 flex cursor-pointer items-center gap-1.5 rounded-full bg-green-500 px-3 py-1.5 text-xs font-medium text-white"
                >
                  cooked! <CheckIcon className="h-4 w-4" />
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
        <Button type="submit">Create User Recipe</Button>
      </div>
    </form>
  );
}
