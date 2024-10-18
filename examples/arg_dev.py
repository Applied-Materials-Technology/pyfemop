#%%
import argparse

parser = argparse.ArgumentParser("Config Parse")
parser.add_argument("config", help="The YAML config file for this run.", type=str)
args = parser.parse_args()
print(args.config)
# %%
