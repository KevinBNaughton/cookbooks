import { Suspense } from 'react';
import { SessionProvider } from 'next-auth/react';
import { fetchCookbooksAsMap } from '@/app/lib/data';
import Randomizer from '@/app/ui/randomizer';


export default async function Page() {
    const cookbooks_map = await fetchCookbooksAsMap();
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
