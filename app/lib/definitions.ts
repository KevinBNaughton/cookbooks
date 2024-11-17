// Set in top level .env file
// Likely set to: "http://127.0.0.1:PORT/"
export const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

export type User = {
  id: string;
  name: string;
  email: string;
  password: string;
  access_token: string;
};

export type Revenue = {
  month: string;
  revenue: number;
};

export type Cookbook = {
  key: string;
  name: string;
  author: string;
};

export type IngredientList = {
  meat: string[];
  produce: string[];
  seafood: string[];
  pantry: string[];
  dairy: string[];
  seafood_and_meat: string[];
  frozen: string[];
  other: string[];
};

export type InstructionStep = {
  step: string;
  details: string[];
};

export type Recipe = {
  _id: string;
  name_of_dish: string;
  serving_size: string;
  page_number: number;
  cookbook_key: string;
  ingredients: IngredientList;
  instructions: InstructionStep[];
  note: string;
};

export type UserRecipe = {
  _id: string;
  cookbook_key: string;
  recipe_id: string;
  user_id: string;
  status: "uncooked" | "cooked!";
  rating: number;
  updated_at: Date;
  note: string;
};

// TODO - Debate if this should be used
export type RecipeWithUserRecipe = {
  user_recipe: UserRecipe;
  recipe: Recipe;
};

export type CookbookField = {
  id: string;
  name: string;
};

export type RecipeForm = {
  id: string;
  cookbook_key: string;
  status: "uncooked" | "cooked!";
};
