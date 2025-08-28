# 🌊 An Honest Account of My Journey While Working on WaveMail

The start was good, I understood the objective of the project well and was able to clearly define the features and clear out some ambiguities.

The first 3-4 days were then spend debugging ChatGPT codes that it spit out when I inputted the assignment description, trying to learn how Langchain, FastAPI, and React really worked, and waiting for Claude's daily limits to reset so I could use the same chat again.

By then it had gotten out of hand and I couldn't even understand what I was doing. I had 3 days left for the deadline and I decided to start over. So I started doing my digging the good ol' fashion way - **documentation**.

## 📚 The Documentation Deep Dive

Langchain's official documentation was very beginner-friendly and the tutorials were simple and spot on. I finally got an idea about what agents and tools really meant and how it does its LLM orchestration practices, or at least the easy version of it. Here are some of the resources that helped me:

- [Introduction to LangChain](https://python.langchain.com/docs/introduction/)
- [LangChain tutorials](https://python.langchain.com/docs/tutorials/)
- [Tutorial - Building an agent](https://python.langchain.com/docs/tutorials/agents/)

With the help of gemini-2.5-pro (through LMArena), I was able to compile a comprehensive guide on the Gmail API that covered areas from fetching emails using various kinds of queries, to modifying labels and sorting emails.

> **Link:** [guides folder](./guides/)

## 🛠️ Building the Core Features

After building a basic fetch tool and testing it out (it worked!!), I decided to start with the first feature - Notifications dashboard. After some GPTing I realised that a **deterministic pipeline** would work and the "tools" won't really be necessary here, so the notifications pipeline only used the underlying function.

```
Fetch → Classify (as important or not) → Summarize (important ones)
```

I created basic classify and summarize tools too, where the classification would happen using a **hybrid rule-based and LLM-based method**, where Groq API (finally) came into play.

The classification tool was a little tough to crack because even marketing emails were classified as important. A little bit of prompt tweaking helped, but it can still be refined.

The to-do pipeline was built in a similar manner: fetch emails and generate to-do list, which was a new tool that used Groq API to obtain action items (if they exist) from emails. Debugging and refining the prompts was funnnnnn (not). I mean, look at this:

<img width="522" height="298" alt="FUN ERRORS" src="https://github.com/user-attachments/assets/d5582c7e-a9a4-459c-82d5-6460ace5bf3c" />

At this point, you could never run out of to-do lists :)

## 🤖 Facing the Scary Part - The Chatbot

And now I decided to face the scary part - building the chatbot and actually making use of LangChain's capabilities. So far I had four tools ready - fetch, summarize, classify, and generate to-do. But the fetch tool was only capable of fetching by number (i.e., fetch the last five emails) and would crash at mentions of anything else, like sender, or date, etc.

So I created another tool - fetch_emails_by_sender! Right thing to do? Nope. It was a temporary solution. The right thing to do was to tweak the existing fetch tool to be able to deal with all kinds of queries. But here we are.

## 💻 The Frontend Disaster

In between all this I thought I'd go ahead and fully vibe-coded a React based frontend when I didn't even understand most of it. That blew up right in my face. Thankfully, I gave up on it quick enough and stuck to my all time favs - vanilla HTML, CSS, JS. *(Disclaimer: All Claude, almost nothing by me)*.

## 📧 Email Sorting Tool

I also created a `sort_email` tool that could either be accessed using a button to sort unimportant emails into categories (updates, forums, etc.) or trash/spam, or be called as a tool by LangChain upon the request of the user. It worked quite alright, it didn't sort all emails correctly but most of them were sorted just fine.

## 🧠 The Prompt Engineering Nightmare

Now came the time to test out different cases and user queries. And it broke my brain. I regretted all the times I disregarded the art of prompt engineering.

The tool descriptions were of EXTREME importance for LangChain to pick the right tools. For a long time I worked out around them and tested them out, but the same requests ended up giving different results. I mean:

<img width="992" height="258" alt="output1" src="https://github.com/user-attachments/assets/64654e95-0f7b-437c-a975-46073528366b" />
<img width="877" height="303" alt="output2" src="https://github.com/user-attachments/assets/e49d3ec3-8757-45af-af97-2920c516701f" />

Both are responses for `"Move all emails from The New York Times to trash"`. Both generated two different action queries and the first one was useful enough for the LLM in the fetch tool to understand the correct email query but the second one resorted to simply fetching all unread emails in the inbox and sorting them accordingly.

## 🔧 Tool Chaining Challenges

Because the agent chain would always end up picking a single tool and then end its chain of action, I had to tweak certain tools to incorporate other necessary steps, such as including a call to the fetch tool's underlying function within the sort tool's function. I made some changes to the description of the function to run the chat. Specifically, I added **ReAct reasoning** under its features:

```
ReAct reasoning: Thought → Action → Observation → Next Thought
```

And then it started to be able to pick multiple tools. Eureka! Or not, because it started nesting tool calls which messed up the inputs passed to tools.

## 🏁 The Final Push

Debugging my way through LLM inputs and outputs while hitting my daily token usage limits on the free tier by Groq (for more than 5 different API keys, mind you 😭) was a looooong process and it still needs a lot of work but for now, it meets all the basic functionalities :))

---

Thanks God, Gemini-2.5-Pro (via LMArena), ChatGPT, and Claude for helping me pull through! 🫶
