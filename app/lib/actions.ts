"use server";

import { z } from "zod";
import { signIn } from "@/auth";
import { AuthError } from "next-auth";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { API_URL, Recipe } from "./definitions";

const FormSchema = z.object({
  id: z.string(),
  rating: z.number(),
  status: z.enum(["uncooked", "cooked!"], {
    invalid_type_error: "Please select a recipe status.",
  }),
  date: z.string(),
});

// const CreateUserRecipe = FormSchema.omit({ id: true, date: true });
const UpdateUserRecipe = FormSchema.omit({ date: true, id: true });

export type State = {
  errors?: {
    status?: string[];
  };
  message?: string | null;
};

export async function updateUserRecipe(
  recipe: Recipe,
  _prevState: State,
  formData: FormData,
) {
  const validatedFields = UpdateUserRecipe.safeParse({
    status: formData.get("status"),
    rating: formData.get("rating"),
  });
  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
      message: "Missing Fields. Failed to Update Recipe.",
    };
  }
  const { status, rating } = validatedFields.data;
  console.debug(
    `Got status: ${status} and rating: ${rating} for Recipe ID: ${recipe._id}`,
  );

  try {
    const update = await fetch(`${API_URL}/api/recipes/user/${recipe._id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ status, rating }),
    });
    console.info("Updated Recipe: ", await update.json());
  } catch (error) {
    console.error("Server Error", error);
    throw new Error(`Failed to Update recipe: ${recipe._id}`);
  }

  revalidatePath("/dashboard/recipes");
  redirect("/dashboard/recipes");
}

export async function authenticate(
  _prevState: string | undefined,
  formData: FormData,
) {
  try {
    await signIn("credentials", formData);
  } catch (error) {
    if (error instanceof AuthError) {
      switch (error.type) {
        case "CredentialsSignin":
          return "Invalid credentials.";
        default:
          return "Something went wrong.";
      }
    }
    throw error;
  }
}
