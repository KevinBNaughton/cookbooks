import { fetchCookbooks } from '@/app/lib/data';
import { Cookbook } from '@/app/lib/definitions';
import Randomizer from '@/app/ui/randomizer';
import { Suspense } from 'react';
import { SessionProvider } from 'next-auth/react';


export default async function Page() {
    const cookbooks = await fetchCookbooks();
    let cookbooks_map: { [key: string]: Cookbook; } = {};
    for (var cookbook of cookbooks) {
        cookbooks_map[cookbook.key] = cookbook;
    };
    return (
        <SessionProvider>
            <div>
                <Suspense>
                    <Randomizer cookbooks_map={cookbooks_map} />
                </Suspense>
            </div>
        </SessionProvider>
    );
}
