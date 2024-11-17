'use client';

import { Cookbook, Recipe } from '@/app/lib/definitions';
import { ViewRecipe } from '@/app/ui/recipes/buttons';
import { useState } from 'react';
import { lusitana } from '@/app/ui/fonts';
import { fetchNRecipes } from '@/app/lib/data';
import { Button } from '@/app/ui/button';
import { useSession } from 'next-auth/react';


export default function Randomizer({
  cookbooks_map,
}: {
  cookbooks_map: { [key: string]: Cookbook; };
}) {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [count, setCount] = useState(1);
  const session = useSession();

  const handleRandomize = async () => {
    try {
      // TODO - Update to be a better randomizer lol
      const recipes = await fetchNRecipes(count, session.data?.accessToken);
      setRecipes(recipes);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };
  return (
    <div className="w-full">
      <h1 className={`${lusitana.className} text-2x1`}>RANDOMIZER</h1>
      <div className="flex w-full items-center justify-between">
        <p>Number of random recipes &rArr;</p>
        <input
          type="number"
          value={count.toString()}
          onChange={(e) => {
            setCount(Number(e.target.value));
          }}
          min="1"
          max="21"
          placeholder="Number random recipes"
          style={{ marginBottom: '10px', width: '100px' }}
        />
      </div>
      <Button className="mt-4 w-full" onClick={handleRandomize} >
        Random Recipe!
      </Button>
      <br />
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', justifyContent: 'center' }}>
        {recipes.map((recipe) => (
          <div key={recipe._id} style={{ border: '1px solid #ccc', padding: '15px', width: '300px' }}>
            <div>
              <h2><strong>{recipe.name_of_dish}</strong></h2>
              <h4>{cookbooks_map[recipe.cookbook_key].name}</h4>
              <h4>{cookbooks_map[recipe.cookbook_key].author}</h4>
              <p>Page {recipe.page_number}</p>
              <div className="flex justify-start gap-3">
                <ViewRecipe id={recipe._id} />
              </div>
            </div>
            <br />
            {Object.values(recipe.ingredients).map((value, index) =>
              value.length > 0 ? (
                <div key={recipe._id + index}>
                  {
                    Object.values(value).map(val =>
                      val.length > 0 ? (
                        <p key={recipe._id + val}>{val}</p>
                      ) : null)}
                </div>
              ) : null)}
          </div>
        ))}
      </div>
    </div >
  );
}
