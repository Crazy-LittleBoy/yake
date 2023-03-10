from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import yake

app = FastAPI()
YAKES = dict()


class YakeRequest(BaseModel):
    text: str
    language: str
    max_ngram_size: int
    number_of_keywords: int
    windows_size: int


async def extract_keywords_async(text, language, max_ngram_size, number_of_keywords, windows_size):
    my_yake = YAKES.get(language, None)
    if my_yake is None:
        my_yake = yake.KeywordExtractor(lan=language,
                                        n=max_ngram_size,
                                        top=number_of_keywords,
                                        dedupLim=0.9,
                                        windowsSize=windows_size)
        YAKES[language] = my_yake
    keywords = my_yake.extract_keywords(text)
    return [{"keyword": x[0], "score": x[1]} for x in keywords]


@app.post("/yake/")
async def handle_yake(request: YakeRequest):
    try:
        assert request.text, "Invalid text"
        assert len(request.language) == 2, "Invalid language code"
        assert int(request.max_ngram_size), "Invalid max_ngram_size, Suggested max_ngram_size setting of 1 or 2 or 3"
        assert int(request.number_of_keywords), "Invalid number_of_keywords"
        assert int(request.windows_size), "Invalid windows_size, Suggested windows_size setting of 1 or 2"
        # print(request)
        # print('YAKES: %s \n' % YAKES)
        text = request.text
        language = request.language
        max_ngram_size = int(request.max_ngram_size)
        number_of_keywords = int(request.number_of_keywords)
        windows_size = int(request.windows_size)
        keywords = await extract_keywords_async(text, language, max_ngram_size, number_of_keywords, windows_size)
        return JSONResponse(content=keywords)
    except AssertionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IOError as e:
        raise HTTPException(status_code=400, detail="Language not supported")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        app,
        # 'yake-rest-api:app',
        host="0.0.0.0",
        port=5000,
        # workers=2,
        # reload=True
    )
