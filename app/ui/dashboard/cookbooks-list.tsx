import { lusitana } from '@/app/ui/fonts';
import { fetchCookbooks } from '@/app/lib/data';
import { Cookbook } from '@/app/lib/definitions';

export default async function CookbookList() {
  const cookbooks: Cookbook[] = await fetchCookbooks();
  if (!cookbooks || cookbooks.length === 0) {
    return <p className="mt-4 text-gray-400">No cookbooks available.</p>;
  }

  return (
    <div className="w-full md:col-span-4">
      <h2 className={`${lusitana.className} mb-4 text-xl md:text-2xl`}>
        Cookbooks
      </h2>
      <div className="rounded-xl bg-gray-50 p-4">
        {cookbooks.map(cookbook => (
          <div key={cookbook.key} className="sm:grid-cols mt-0 grid grid-cols items-end gap-4 rounded-md bg-white p-4 md:gap-4">
            <div key={cookbook.key} className="flex flex-col items-center gap-4">
              <p>{cookbook.name}</p>
              <p>{cookbook.author}</p>
              {/* <div>{cookbook.key}</div> */}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
