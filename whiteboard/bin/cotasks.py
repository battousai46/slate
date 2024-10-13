import httpx
import asyncio


async def get_episode(client, url):
    return await client.get(url)


async def cotasks(timeout=60):
    url_endpoint: str = "https://rickandmortyapi.com/api/episode/{episode_id}"
    episodes = 10
    urls = [url_endpoint.format(episode_id=(x + 1)) for x in range(episodes)]
    async with httpx.AsyncClient(timeout=timeout) as client:
        tasks = []
        async with asyncio.TaskGroup() as tg:
            for url in urls:
                task = tg.create_task(get_episode(client, url))
                tasks.append(task)

        results = [ task.result() for task in tasks ]
        for ret in results:
            print(ret.json())



if __name__ == "__main__":
    asyncio.run(cotasks())
