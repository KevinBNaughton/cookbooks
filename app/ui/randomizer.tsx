"use client";

import { Cookbook, Recipe } from "@/app/lib/definitions";
import { ViewRecipe } from "@/app/ui/recipes/buttons";
import { useState } from "react";
import { lusitana } from "@/app/ui/fonts";
import { fetchNRecipes } from "@/app/lib/data";
import { Button } from "@/app/ui/button";
import { signOut } from "next-auth/react";
import RecipeStatus from "./recipes/status";
import RecipeRating from "./recipes/rating";

export default function Randomizer({
  cookbooks_map,
}: {
  cookbooks_map: { [key: string]: Cookbook };
}) {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [count, setCount] = useState(1);

  const handleRandomize = async () => {
    try {
      // TODO - Update to be a better randomizer lol
      const recipes = await fetchNRecipes(count);
      if (!recipes) {
        signOut();
        return;
      } else {
        setRecipes(recipes);
      }
    } catch (error) {
      console.error("Error fetching data:", error);
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
          style={{ marginBottom: "10px", width: "100px" }}
        />
      </div>
      <Button className="mt-4 w-full" onClick={handleRandomize}>
        Random Recipe!
      </Button>
      <br />
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "20px",
          justifyContent: "center",
        }}
      >
        {recipes.map((recipe) => (
          <div
            key={recipe._id}
            style={{
              border: "1px solid #ccc",
              padding: "15px",
              width: "300px",
            }}
          >
            <div>
              <div className="flex flex-row justify-start">
                <h2 className="basis-5/6">
                  <strong>{recipe.name_of_dish}</strong>
                </h2>
                <div className="basis-1/6 pl-2 flex flex-col justify-start items-center">
                  <ViewRecipe id={recipe._id} />
                </div>
              </div>
              <div className="flex flex-row gap-3 pt-2 pb-2">
                <div className="basis-3/5 flex flex-col">
                  <h4>{cookbooks_map[recipe.cookbook_key].name}</h4>
                  <h4>{cookbooks_map[recipe.cookbook_key].author}</h4>
                  <p>Page {recipe.page_number}</p>
                </div>
                <div className="basis-2/5 flex flex-col justify-start">
                  <div className="flex justify-end">
                    <RecipeStatus
                      status={recipe?.user_recipe?.status || "uncooked"}
                    />
                  </div>
                  <div className="flex justify-end items-center">
                    <RecipeRating
                      initial_rating={recipe?.user_recipe?.rating || 0}
                      readonly={true}
                      is_rtl={true}
                    />
                  </div>
                </div>
              </div>
            </div>
            <br />
            {Object.values(recipe.ingredients).map((value, index) =>
              value.length > 0 ? (
                <div key={recipe._id + index}>
                  {Object.values(value).map((val) =>
                    val.length > 0 ? <p key={recipe._id + val}>{val}</p> : null,
                  )}
                </div>
              ) : null,
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
