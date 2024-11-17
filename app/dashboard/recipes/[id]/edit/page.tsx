import Form from '@/app/ui/recipes/edit-form';
import Breadcrumbs from '@/app/ui/recipes/breadcrumbs';
import { fetchRecipeById, fetchCookbooks, fetchUserRecipeById } from '@/app/lib/data';
import { auth } from "@/auth"
import { notFound } from 'next/navigation';


export default async function Page(props: { params: Promise<{ id: string }> }) {
	const params = await props.params;
	const id = params.id;
	const session = await auth();
	const [recipe, cookbooks, user_recipe] = await Promise.all([
		fetchRecipeById(id),
		fetchCookbooks(),
		fetchUserRecipeById(id, session?.accessToken),
	]);
	if (!recipe || !user_recipe) {
		notFound();
	}
	return (
		<main>
			<Breadcrumbs
				breadcrumbs={[
					{ label: 'Recipes', href: '/dashboard/recipes' },
					{
						label: 'Edit Recipe',
						href: `/dashboard/recipes/${id}/edit`,
						active: true,
					},
				]}
			/>
			<Form recipe={recipe} cookbooks={cookbooks} user_recipe={user_recipe} />
		</main>
	);
}
