export async function getCategories(token) {
    console.debug("Calling fetch...");
    const r = await fetch(window.location.origin + "/backend/categories",
        {
            headers: {
                Accept: 'application/json',
                Authorization: `Bearer ${token}`
            }
        }
    );
    console.debug("Fetch await done, calling json await...");
    const json = await r.json();
    console.debug("json await done");
    return json
}
