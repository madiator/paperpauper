Summarizes papers (PDFs) into structured format.

See this example: https://curator.bespokelabs.ai/datasets/26d4adb10ab6445687b085bd28f5aec0?appId=3fb0753708f042718c36775d92b9fa71

Note that if you enable CURATOR_VIEWER (which is enabled by default -- see the .env file),
the outputs are streamed to the viewer, which improves the visualization of the outputs.

The URL of the viewer is displayed in the terminal.

The data can be transformed into a nicer view, by adding an appId to the URL (which is done below).
If you are interested more about creating custom visualizations or want to change the structured outputs here, 
please contact me (mahesh at bespokelabs.ai).

Other things to note:
* Caching is enabled by default. So if the prompt and/or the input doesn't change,
  the output is served from the cache.
* If you want to disable caching, you can set the environment variable
  CURATOR_DISABLE_CACHE=1.

Installation:
```shell
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python summarize.py
```