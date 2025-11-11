# ============================================================================
# MCP CLIENT - STDIO MCP Server Client with LangChain and Ollama
# ============================================================================
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio

# Global variable to hold the session
SESSION = None
TOOLS = None

# Initialize Ollama LLM
llm = ChatOllama(
    model="granite3.2:8b",  # Change to your preferred model (gemma3 doesn't support tools)
    temperature=0
)

# Define the agent prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful video editing assistant. You have access to various video editing tools.
    
Available tools:
- download_youtube_video: Download videos from YouTube
- trim_video: Trim videos based on timestamps
- merge_videos: Merge two videos together
- extract_audio: Extract audio from video files
- trim_audio: Trim audio files based on timestamps
- convert_video_format: Convert videos to different formats
- add_watermark: Add watermarks to videos
- extract_frames: Extract frame image from videos at specified time intervals
- change_audio_speed: Change the speed of audio tracks
- change_video_speed: Change the speed of video playback
- mute_video_audio: Remove audio from videos making them muted
- create_gif: Create GIFs from videos

When users ask for audio or video editing tasks, use the appropriate tools to help them.
Always provide the full file paths in your responses."""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

async def setup_mcp_client():
    global SESSION, TOOLS

    """Setup MCP client connection to MCP server"""
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            SESSION = session
            # List available tools
            tools_list = await session.list_tools()
            
            # Convert MCP tools to LangChain tools
            langchain_tools = []
            for tool in tools_list.tools:
                # Create a wrapper function for each tool
                async def call_tool(tool_name=tool.name, **kwargs):
                    result = await session.call_tool(tool_name, arguments=kwargs)
                    return result.content[0].text if result.content else "No result"
                
                langchain_tools.append(
                    Tool(
                        name=tool.name,
                        func=lambda tn=tool.name, **kwargs: asyncio.run(call_tool(tn, **kwargs)),
                        description=tool.description or f"Tool: {tool.name}"
                    )
                )
            TOOLS = langchain_tools
            return langchain_tools

async def run_agent(user_input: str):
    """Run the agent with user input"""
    global TOOLS
    # Create agent using create_react_agent
    agent = create_agent(llm, TOOLS)
    
    # Run agent
    result = agent.invoke({"messages": [("user", user_input)]})
    return result

# Example usage
if __name__ == "__main__":
    # Setup MCP client and tools
    asyncio.run(setup_mcp_client())

    # Example queries
    queries = [
        "Download this YouTube video: https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "Trim the downloaded video from 00:00:10 to 00:00:30",
        "Extract audio from the trimmed video",
        "Create a GIF from the first 5 seconds of the video"
    ]
    
    print("Audio Video Editor MCP Client with LangChain + Ollama\n")
    print("=" * 60)
    
    # Interactive mode
    while True:
        user_input = input("\nWhat would you like to do? (or 'quit' to exit): ")
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        try:
            result = asyncio.run(run_agent(user_input))
            # Handle the result from the agent
            if isinstance(result, dict):
                if 'output' in result:
                    print(f"\nResult: {result['output']}")
                elif 'messages' in result:
                    for msg in result['messages']:
                        if hasattr(msg, 'content'):
                            print(f"\nResult: {msg.content}")
                else:
                    print(f"\nResult: {result}")
            else:
                print(f"\nResult: {result}")
        except Exception as e:
            print(f"Error: {str(e)}")