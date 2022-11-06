import os
from discord.ext import commands
import discord
from dotenv import load_dotenv
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import traceback


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN_TESTING')
intents = discord.Intents.default()
intents.guild_messages= True
intents.dm_messages=True
intents.messages=True
intents.presences=True
bot = commands.Bot(command_prefix='$',help_command=None,intents=intents)
bot.remove_command('help')

@bot.command(name='help')
async def help(ctx):
    embed = discord.Embed(title="Help")
    embed.add_field(name="$graph",value="Generates pre-req graph for given course with an optional number of layers.\n\n$graph <campus> <dept> <code> <layers>\n\nExamples:\n>>   $graph UBCO COSC 499 2\n>>  $graph ubc engl 366")
    embed.add_field(name="$csv",value="Sends csv of course data.\n\nExample:\n>>  $csv")
    embed.set_footer(text="This bot was created by: JEFF#1778")
    print("help")
    await ctx.send(embed=embed)

@bot.command(name='csv')
async def send_data(ctx):
    print("csv")
    await ctx.send(file=discord.File("courses.csv"))

@bot.command(name='graph')
async def course_search(ctx,*,content:str):
    content = content.upper()
    df = pd.read_csv("courses.csv")
    max_nodes = 20
    num_layers = float('inf')
    trimmed_for_space = False
    try:
        num_layers = int(content.split(" ")[3])
    except:
        pass

    try:
        G = build_graph(content,df)
    except:
        embed = discord.Embed(title = "Query Error")
        embed.add_field(name = "Course does not exist\nor\nSyntax is wrong", value ="eg.\n$graph UBCO COSC 499\nor\n$graph ubc engl 366")
        embed.set_footer(text="This bot was created by: JEFF#1778")
        await ctx.send(embed=embed)
        traceback.print_exc()
        return

                
    while len(G) > max_nodes:
        G = trim_leaves(G)
        trimmed_for_space = True
    
    while len(list(nx.topological_generations(G))) - 1 > num_layers:
        G = trim_leaves(G)
        trimmed_for_space = False


    pos_dict = {}
    for i, node_list in enumerate(nx.topological_generations(G)):
        x_offset = len(node_list) / 2
        y_offset = 0.1
        for j, name in enumerate(node_list):
            pos_dict[name] = (j - x_offset, -i + j * y_offset)


    plt.figure(figsize=(15,15))
    nx.draw(G,pos_dict, with_labels = True,font_size = 12,node_size = 4000,arrowsize = 20,width= 3)
    plt.savefig("graph.png")

    trimmed_msg = ""
    if trimmed_for_space:
        trimmed_msg = "\nThis graph has been trimmed to save space"

    embed = discord.Embed(title = content + " Pre-req graph" + trimmed_msg)
    img = discord.File("graph.png")
    embed.set_image(url="attachment://graph.png")

    for node in G:
        row = df[(df['Campus'] == content.split(" ")[0]) & (df['Department'] == node.split(" ")[0]) & (df['Course code'] == node.split(" ")[1])].iloc[0]
        url = row['URL']
        details = '[View on UBC]('+url+')\n' 
        reqs = str(row['Pre-req string'])
        if reqs == 'nan':
            reqs = "Pre-reqs: None"
            
        details = details + reqs
        embed.add_field(name = node, value = details)
    
   
    embed.set_footer(text="This bot was created by: JEFF#1778")
    print(content)
    await ctx.send(file=img,embed=embed)


def trim_leaves(G):
    node_degrees = G.in_degree()
    leaves = list()
    for node,deg in node_degrees:
        if deg == 0:
            leaves.append(node)

    G.remove_nodes_from(leaves)
    return G


def build_graph(query,df):   
    G = nx.DiGraph()
    return traverse(query,df,G)

def traverse(query,df,G):
    split_q = query.split(" ")
    campus = split_q[0]
    dept = split_q[1]
    code = split_q[2]
    this_node = dept + " " + code

    G.add_node(this_node)
    
    row = df[(df['Campus'] == campus) & (df['Department'] == dept) & (df['Course code'] == code)].iloc[0]
      
    pre_reqs = str(row['Pre-reqs']).split(',')

    if pre_reqs[0] != 'nan':

        for pre_req in pre_reqs:           
           
            pre_req_dept = pre_req.split(" ")[0]
            pre_req_code = pre_req.split(" ")[1]
            
            if len(df[(df['Campus'] == campus) & (df['Department'] == pre_req_dept) & (df['Course code'] == pre_req_code)])!=0:
                G.add_node(pre_req)
                G.add_edge(pre_req,this_node)
                sub_query = campus + " " + pre_req_dept + " " + pre_req_code
                traverse(sub_query,df,G)

    return G


bot.run(TOKEN)
