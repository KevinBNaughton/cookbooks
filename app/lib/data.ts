"use server";
import { Cookbook, API_URL, Recipe, UserRecipe } from "@/app/lib/definitions";
import { auth } from "@/auth";
import { APIAuthError } from "./errors";

export async function buildAuthorizationHeaders(
  headers: { [key: string]: string } = {},
): Promise<HeadersInit> {
  const session = await auth();
  if (session?.accessToken) {
    headers["Authorization"] = `Bearer ${session?.accessToken}`;
  }
  return headers;
}

export async function fetchCookbooks(): Promise<Cookbook[]> {
  try {
    const data = await fetch(API_URL + "api/cookbooks");
    let cookbooks = await data.json();
    // console.debug("Cookbooks: ", cookbooks);
    return cookbooks.cookbooks;
  } catch (error) {
    console.error("Server Error:", error);
    throw new Error("Failed to fetch cookbooks.");
  }
}

export async function fetchCookbooksAsMap(): Promise<{
  [key: string]: Cookbook;
}> {
  const cookbooks = await fetchCookbooks();
  let cookbooks_map: { [key: string]: Cookbook } = {};
  for (var cookbook of cookbooks) {
    cookbooks_map[cookbook.key] = cookbook;
  }
  return cookbooks_map;
}

export async function fetchRecipesForCookbook(cookbook: Cookbook) {
  try {
    const data = await fetch(API_URL + "api/recipes/" + cookbook.key);
    let recipes = await data.json();
    // console.debug("Number of recipes: ", recipes.len());
    return recipes.recipes;
  } catch (error) {
    console.error("Server Error:", error);
    throw new Error("Failed to fetch recipes for cookbook: " + cookbook.key);
  }
}

export async function fetchNRecipes(count: number) {
  try {
    const data = await fetch(API_URL + "api/recipes/random/" + count, {
      headers: await buildAuthorizationHeaders(),
    });
    let recipes = await data.json();
    // console.debug("Number of recipes: ", recipes.length);
    // console.debug("recipes: ", recipes.recipes);
    return recipes.recipes;
  } catch (error) {
    console.error("Server Error:", error);
    throw new Error("Failed to fetch n random recipes");
  }
}

export async function fetchCardData() {
  try {
    const cookbooksCountPromise = fetch(API_URL + "api/cookbooks/count");
    const recipesCountPromise = fetch(API_URL + "api/recipes/count");
    const data = await Promise.all([
      cookbooksCountPromise,
      recipesCountPromise,
    ]);
    const cookbooksCountJsonPromise = data[0].json();
    const recipesCountJsonPromise = data[1].json();
    const json_data = await Promise.all([
      cookbooksCountJsonPromise,
      recipesCountJsonPromise,
    ]);

    const numberOfCookbooks = Number(json_data[0].count ?? "0");
    const numberOfRecipes = Number(json_data[1].count ?? "0");
    // console.debug(
    //   "cookbooks: " + numberOfCookbooks + " recipes: " + numberOfRecipes,
    // );

    return {
      numberOfCookbooks,
      numberOfRecipes,
    };
  } catch (error) {
    console.error("API Error:", error);
    throw new Error("Failed to fetch card data.");
  }
}

const ITEMS_PER_PAGE = 30;
export async function fetchFilteredRecipes(
  query: string,
  status: "" | "cooked!" | "uncooked",
  currentPage: number,
): Promise<Recipe[]> {
  // const offset = (currentPage - 1) * ITEMS_PER_PAGE;
  // console.debug("Query: ", query);
  // "?cookbook=" +
  // cookbook.key +
  try {
    let url = API_URL + "api/recipes";
    let url_params = new URLSearchParams();
    if (query.length > 0) {
      url_params.set("query", query);
    }
    if (status.length > 0) {
      url_params.set("status", status);
    }
    if (url_params.size > 0) {
      url += "?";
      url += url_params.toString();
    }
    const data = await fetch(url, {
      headers: await buildAuthorizationHeaders(),
    });
    if (data.status == 401) {
      throw new APIAuthError(`Authorization Error: ${data.statusText}`);
    }
    let recipes = await data.json();
    // console.debug("Recipes: ", recipes.recipes);
    return recipes.recipes;
  } catch (error) {
    console.error("API Error:", error);
    if (error instanceof APIAuthError) {
      throw error;
    }
    throw new Error("Failed to fetch filtered recipes.");
  }
}

export async function fetchRecipesPages(query: string): Promise<number> {
  try {
    let url = API_URL + "api/recipes/count";
    let url_params = new URLSearchParams();
    if (query.length > 0) {
      url_params.set("query", query);
    }
    if (url_params.size > 0) {
      url += "?";
      url += url_params.toString();
    }
    const data = await fetch(url);
    let count = await data.json();
    const totalPages = Math.ceil(Number(count.count) / ITEMS_PER_PAGE);
    return totalPages;
  } catch (error) {
    console.error("API Error:", error);
    throw new Error("Failed to fetch total number of recipes.");
  }
}

export async function fetchRecipeById(id: string): Promise<Recipe> {
  try {
    let url = API_URL + "api/recipes/recipe/" + id;
    const data = await fetch(url);
    let recipe = await data.json();
    return recipe;
  } catch (error) {
    console.error("API Error:", error);
    throw new Error("Failed to fetch recipe.");
  }
}

export async function fetchUserRecipeById(id: string): Promise<UserRecipe> {
  try {
    const data = await fetch(`${API_URL}/api/recipes/user/${id}`, {
      headers: await buildAuthorizationHeaders(),
    });
    let user_recipe = await data.json();
    return user_recipe;
  } catch (error) {
    console.error("API Error:", error);
    throw new Error("Failed to fetch user recipe.");
  }
}
