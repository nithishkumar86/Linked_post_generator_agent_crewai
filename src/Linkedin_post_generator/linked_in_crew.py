from crewai import Agent, Task, Crew
from crewai.project import CrewBase, agent, task, crew
from crewai.tools import tool
from src.Crew_flow.config import get_llm
from crewai import Process

@CrewBase
class LinkedInCrew:

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    llm = get_llm()

    @agent
    def content_agent(self) -> Agent:
        
        return Agent(config = self.agents_config["content_agent"]
                     ,llm=self.llm)

    @agent
    def seo_agent(self) -> Agent:
        return Agent(
            config = self.agents_config["seo_agent"],
            llm = self.llm
            )

    @agent
    def post_agent(self) -> Agent:
        return Agent(
            config = self.agents_config["post_agent"],
            llm = self.llm
        )

    # -------- TASKS -------- #

    @task
    def content_task(self) -> Task:
        return Task(
            config = self.tasks_config["content_task"]
        )

    @task
    def seo_task(self) -> Task:
        return Task(config = self.tasks_config["seo_task"])

    @task
    def post_task(self) -> Task:
        return Task(config = self.tasks_config["post_task"])

    # -------- CREW -------- #

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.content_agent(),
                self.seo_agent(),
                self.post_agent()
            ],
            tasks=[
                self.content_task(),
                self.seo_task(),
                self.post_task()
            ],
            verbose=True,
            preocess = Process.sequential
        )


# -------- RUN -------- #

# if __name__ == "__main__":
#     topic = input("Enter LinkedIn post topic: ")

#     result = LinkedInCrew().crew().kickoff(
#         inputs={"topic": topic}
#     )

#     print("\n\n===== FINAL LINKEDIN POST =====\n")
#     print(result)