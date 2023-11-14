FROM python:3.8-slim

WORKDIR /app/backend
COPY . /app/backend

RUN pip3 install gunicorn
RUN pip3 install langchain==0.0.329
RUN pip3 install google-cloud-aiplatform
RUN pip3 install pydantic==1.10.12
RUN pip3 install asyncio
RUN pip3 install fastapi==0.103.2
RUN pip3 install uvicorn
RUN pip3 install pymongo==4.5.0
RUN pip3 install gradio
RUN pip3 install langchainhub==0.1.13
RUN pip3 install langchain_experimental
RUN pip3 install presidio-analyzer
RUN pip3 install presidio_anonymizer
RUN pip3 install langdetect
RUN pip3 install Faker
RUN pip3 install pyvi
RUN pip3 install https://gitlab.com/trungtv/vi_spacy/-/raw/master/packages/vi_core_news_lg-3.6.0/dist/vi_core_news_lg-3.6.0.tar.gz
RUN pip3 install spacy
RUN pip3 install langserve==0.0.27
RUN pip3 install sse_starlette
RUN pip3 install google-search-results
RUN pip3 install openai
RUN pip3 install gptcache
RUN pip3 install pip install chardet
RUN pip3 install google-search-results

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "-k", "uvicorn.workers.UvicornWorker", "app:app"]