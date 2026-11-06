SETUP = '''
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from olist_course import config

pd.set_option("display.max_columns", 60)
pd.set_option("display.width", 200)
sns.set_theme(style="whitegrid")
'''

AI_TIP = '''
> 🤖 **AI 協作方式**：Claude Code 使用者可以直接說「用 {skill} skill 幫我…」或呼叫 subagent `{agent}`；
> Codex 使用者說「依照 .agents/skills/{skill}/SKILL.md 的流程…」。
> **規則**：AI 產生的每個數字，你都要能指出是哪一行程式算出來的。
'''
