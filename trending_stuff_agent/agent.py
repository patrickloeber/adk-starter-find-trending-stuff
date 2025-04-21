from typing import Optional

import requests
from bs4 import BeautifulSoup

from google.adk.agents import Agent


def get_hackernews_posts(number_of_posts: Optional[int] = None):
    """
    Gets the top hackernews posts and extracts top post titles and links.

    Args:
        number_of_posts: The number of posts to return. If None, returns all posts.

    Returns:
        dict: status and result. In case of success, it contains a posts field with a
        list of dictionaries, where each dictionary contains the 'title' and 'link' of a post.
    """

    try:
        res = requests.get("https://news.ycombinator.com/")

        soup = BeautifulSoup(res.content, "html.parser")

        posts = []

        # Find all table rows with class 'athing' - these contain the posts
        post_rows = soup.find_all("tr", class_="athing")

        for row in post_rows:
            # Find the span with class 'titleline' within the row
            title_span = row.find("span", class_="titleline")

            if title_span:
                # Find the anchor tag (<a>) within the title span
                link_tag = title_span.find("a")
                if link_tag and link_tag.has_attr("href"):
                    title = link_tag.get_text(strip=True)
                    link = link_tag["href"]
                    posts.append({"title": title, "link": link})

        if number_of_posts is not None:
            posts = posts[:number_of_posts]

        return {
            "status": "success",
            "posts": posts,
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error when trying to get hackernews posts: {e}",
        }


def get_github_trending_repos(number_of_repos: Optional[int] = None):
    """
    Gets the trending github repos and extracts repo name and link.

    Args:
        number_of_repos: The number of repos from the trending page to return. If None, returns all repos.

    Returns:
        dict: status and result. In case of success, it contains a repos field with a
        list of dictionaries, where each dictionary contains the 'title' and 'link' of a post.
    """

    try:
        res = requests.get("https://github.com/trending")

        soup = BeautifulSoup(res.content, "html.parser")
        repos = []

        # Find all article elements which contain repository info
        # Updated selector based on the provided HTML structure
        repo_articles = soup.find_all("article", class_="Box-row")

        for article in repo_articles:
            # Find the h2 tag containing the link
            h2_tag = article.find("h2", class_="h3")
            if not h2_tag:
                continue  # Skip if structure is unexpected

            link_tag = h2_tag.find("a")
            if link_tag and link_tag.has_attr("href"):
                relative_link = link_tag["href"]
                full_link = f"https://github.com{relative_link}"

                # Extract and clean the title text (owner / repo_name)
                # Use .stripped_strings to get text parts and join them
                title_parts = list(link_tag.stripped_strings)
                if len(title_parts) >= 2:
                    # Join the parts, assuming the format is like ['owner', '/', 'repo_name']
                    # or just ['owner / repo_name'] after stripping
                    title = " ".join(title_parts).replace(
                        " ", ""
                    )  # Aims for "owner/repo_name"
                else:
                    title = (
                        link_tag.get_text(strip=True).replace("\n", "").replace(" ", "")
                    )

                repos.append({"title": title, "link": full_link})

        if number_of_repos is not None:
            repos = repos[:number_of_repos]

        return {
            "status": "success",
            "repos": repos,
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error when trying to get trending repos: {e}",
        }


root_agent = Agent(
    name="hackernews_agent",
    model="gemini-2.5-flash-preview-04-17", # "gemini-2.5-pro-exp-03-25"
    description=("Agent to get the top hackernews posts and trending github repos"),
    instruction=("I can get the top hacker news posts and the trending github repos"),
    tools=[get_hackernews_posts, get_github_trending_repos],
)
