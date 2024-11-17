import { Cookbook, API_URL, Recipe, UserRecipe } from "@/app/lib/definitions";

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

export async function fetchNRecipes(count: number, token: undefined | string) {
  try {
    const data = await fetch(API_URL + "api/recipes/random/" + count, {
      headers: {
        Authorization: "Bearer " + token,
      },
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
  currentPage: number,
): Promise<Recipe[]> {
  // const offset = (currentPage - 1) * ITEMS_PER_PAGE;
  // console.debug("Query: ", query);
  // "?cookbook=" +
  // cookbook.key +
  try {
    let url = API_URL + "api/recipes";
    if (query.length > 0) {
      url += "/search" + "?query=" + query;
    }
    const data = await fetch(url);
    let recipes = await data.json();
    // console.debug("Recipes: ", recipes.recipes);
    return recipes.recipes;
  } catch (error) {
    console.error("API Error:", error);
    throw new Error("Failed to fetch filtered recipes.");
  }
}

export async function fetchRecipesPages(query: string): Promise<number> {
  try {
    let url = API_URL + "api/recipes/count";
    if (query.length > 0) {
      url += "/search" + "?query=" + query;
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

export async function fetchUserRecipeById(
  id: string,
  token: undefined | string,
): Promise<UserRecipe> {
  try {
    const data = await fetch(`${API_URL}/api/recipes/user/${id}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    let user_recipe = await data.json();
    return user_recipe;
  } catch (error) {
    console.error("API Error:", error);
    throw new Error("Failed to fetch user recipe.");
  }
}
