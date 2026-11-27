### ReporTOON

https://pharmasug.org/proceedings/2026/TT/PharmaSUG-2026-TT-241.pdf

Load outputs into LLM-AI might consume a lot of token, the above paper proposed a solution - TOON(Token-Oriented Object Notation), to contain more strcutured sas dataset;          
<img width="708" height="153" alt="image" src="https://github.com/user-attachments/assets/193f13c7-87fc-4617-8529-386b1a30df0b" />


**Goal: Now, explore a similar way to make LLM read RTF in an efficient way, cost less token and do not lose any raw info.**

Why Do We Need a Parser for Clinical Outputs RTF? 
- 1.Reduce token usage and cost: Raw RTF contains extensive formatting information and redundant codes, consuming unnecessary tokens and increasing costs.
- Manage context limitations: Clinical tables and listings can span hundreds of pages in a single file. Even a RTF with dozen pages may easily exceed an LLM’s context limit, so the model may not capture all the information.

**Why might this be an unavoidable challenge when using LLMs to process outputs?** The underlying challenge: RTF is designed for human-presentation, while LLMs process tokens within a limited context window. A parser helps bridge this gap.

Note: RTF integrated with LLM must be restricted to private Enterprise LLM instances(e.g., Azure OpenAI), not allowed to integrated with outside LLM. 

### 1. Create a solid parser -  convert RTF to toon
- Reatain title, footnote, header, footer, column, row label&values, indentation, blank row,grid line, alignment space, page into toon file;
- Able to handle all RTF egnerated by SAS `ODS RTF PROC REPORT`, but limited to table&listings, no figure.
- File size of toon should be reduced significantly compared with RTF, this is an early sign of lower token usage;


### 2. Assess the conversion is realiable
Firstly, assess the conversion is realiable and do not lose the key raw info of RTF, the toon would also reatin the layout info and enable we can restore back to RTF soley rely on converted toon file, This process is not intended for LLM use. It simply restores the TOON file to RTF to verify that no information was lost, confirm the reliability of the conversion, and support potential retrospective checks.

Secondly, ensure Toon based on solid strcuture that contains all and same information as RTF, LLM can understand the toon as well as RTF.

### 3. Benchmark
Pick some RTF files for benchmark testing to **quantify the reduction in token usage**. Here it just compare the token-consuming between RTF&toon, the (previous work)[https://github.com/toon-format/toon#using-toon-with-llms] has demonstrated that toon is a more efficient and reliable format than JSON or YAML for LLM data processing.

Two mainstream LLM models(GPT 5.4, GPT6-Astra)



#### 3.1 Tokenizer Computation

Here, we use $D_{\\text{RTF}}$ as a measure of RTF information density.

$$D_{\\text{RTF}} = \\frac{\\text{RTF File Size (KiB)}}{\\text{Number of Pages in the Original Report}}$$

Token usage decreased across all tested files, with per-file reductions ranging from 51.21% to 86.96%. The overall token reduction was 77.83%, while the median per-file reduction was 68.52%. Most tested files achieved reductions between 50% and 70%


<img width="9600" height="2800" alt="gpt54sidebyside800dpi" src="https://github.com/user-attachments/assets/74be0e5c-5ff2-4c51-b310-3f9c6d26bf20" />


| $D_{\\text{RTF}}$ Range (KiB/page) | Number of Files | Median Token Reduction |
|--------------------|-----------------|------------------------|
| 3.39–8.27          | 45              | 53.8%                 |
| 8.33–10.68         | 46              | 62.6%                 |
| 10.70–15.58        | 46              | 66.8%                 |
| 15.72–31.65        | 46              | 73.2%                 | 


#### 3.2 LLM prompts for benchmark:
  
  Q1.Please validate the percentage based on re-calculation of n/N from outputs, or validate statistical results of n, percentage, mean, SD, CI, Min, Max to detect abnormal numbers if possible.
  
  Q2:Please cross check the N&population across multiple tables.
  
  Q3:Please check the consistency of title/footnote.

  Q4:How many columns, treatment group in target table, please list the N number.

  Q5:There are 3 incorrect calculation of percentagaes in target table, please list them.


