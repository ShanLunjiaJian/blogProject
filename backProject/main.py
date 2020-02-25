import json
import os
import time
from fastapi import FastAPI
from pyDatabase import database
import uvicorn
from pydantic import BaseModel

sortItems = "Python C++ Javascript Algorithm ProgrammingLife".split(" ")

app = FastAPI()
BASEDIR = os.path.dirname(__file__)
db = database.Database(os.path.join(BASEDIR, "db.sqlite3"))


def datasToArr(blogs):
    datas = []
    for blog in blogs:
        datas.append({
            "title": blog.title,
            "id": blog.id,
            "user": blog.user,
            "date": blog.date,
            "tag": blog.tag
        })
    return datas

class postNewBlogArg(BaseModel):
    tag: int
    inner: str
    user: int
    title: str


@app.post("/blog/new")
async def postNewBlogApi(item: postNewBlogArg):
    date = time.strftime("%Y-%m-%d")
    currentTime = int(time.time())
    db.create("blog", tag=item.tag, inner=item.inner, user=item.user,
              date=date, time=currentTime, title=item.title)
    return {"message": "success"}


class postNewGoodArg(BaseModel):
    user: int
    id: int


@app.post("/blog/good")
async def postNewGoodApi(item: postNewGoodArg):
    pls = db.filter("pl", id=item.id)
    if len(pls) == 1:
        pl = pls.first()
        if item.user == pl.userId:
            return {
                "message": "self"
            }

        if len(db.filter("good", plId=item.id)) != 0:
            return {
                "message": "repeat"
            }

    db.create("good", plId=item.id, userId=item.user)
    return {"message": "success"}


class postNewPlArg(BaseModel):
    user: int
    inner: str
    blog: int


@app.post("/blog/pl")
async def postNewPlApi(item: postNewPlArg):
    date = time.strftime("%Y-%m-%d")
    db.create("pl", userId=item.user, blogId=item.blog,
              inner=item.inner, date=date)
    return {"message": "success"}


class postSignUpArg(BaseModel):
    username: str
    nickname: str
    password: str


@app.post("/user/signUp")
async def postSignUpApi(item:postSignUpArg):
    if len(db.filter("user",username=item.username))!=0:
        return {"message":"username repeat"}
    db.create("user",username=item.username,nickname=item.nickname,password=item.password)
    return {"message":"success"}

class postSignInArg(BaseModel):
    username:str
    password:str

@app.post("/user/signIn")
async def postSignInApi(item:postSignInArg):
    v_user=db.filter("user",username=item.username)
    if len(v_user)!=1:
        return {"message":"failed"}
    user=v_user.first()
    if user.password==item.password:
        return {"message":"success"}
    else:
        return {"message":"failed"}

class putChangeQmArg(BaseModel):
    id:int
    qm:str

@app.put("/user/changeQm")
async def putChangeQmApi(item:putChangeQmArg):
    user=db.filter("user",id=item.id)
    if len(user)==1:
        user=user[0]
    else:
        return {"message":"the id is wrong"}
    user.qm=item.qm
    user.save()

class putChangePasswordArg(BaseModel):
    id:int
    oldPassword:str
    newPassword:str
@app.put("/user/changePassword")
async def putChangePasswordApi(item:putChangePasswordArg):
    v_user=db.filter("user",id=item.id)
    if len(v_user)!=1:
        return {"message":"the id is wrong"}
    user=v_user[0]
    if user.password==item.oldPassword:
        user.password=item.newPassword
        user.save()
        return {"message":"success"}
    else:
        return {"message":"the password is wrong"}




@app.get("/page/home")
async def getHomeDataApi(num:int):
    blogs = db.filterNum("blog", "time", reverse=True, num=num)
    datas = datasToArr(blogs)
    data={
        "message":"success",
        "sortItems":sortItems,
        "newBlogs":datas
    }
    return data
@app.get("/page/tag")
async def getTagDataApi(tagName:str):
    blogs=db.filter("blog",tag=sortItems.index(tagName))
    datas=datasToArr(blogs)
    return {
        "message":"success",
        "blogs":datas
    }
@app.get("/page/user")
async def getUserDataApi(id:int=None,username:str=None):
    if id==username==None:
        return {
            "message":"arg failed"
        }
    if id!=None:
        user=db.filter("user",id=id)
    elif username!=None:
        user=db.filter("user",username=username)
    if len(user)!=0:
        user=user[0]
        blogs=db.filter("blog",user=user.id)
        blogsData=datasToArr(blogs)
        return {
            "userInfo":{
                "username":user.username,
                "nickname":user.nickname,
                "id":user.id,
                "qm":user.qm,
                "exp":user.exp,
                "k":user.k
            },
            "blogs":blogsData,
            "message":"success"
        }
    else:
        return {"message":"the id or username is wrong"}
@app.get("/page/blog")
async def getBlogDataApi(id:int):
    v_blog=db.filter("blog",id=id)
    if len(v_blog)!=1:
        return {"message":"the id is wrong"}
    blog=v_blog[0]
    d_pl=db.filter("pl",blogId=blog.id)
    pls=[]
    for dp in d_pl:
        pls.append({
            "user":db.get("user",id=dp.userId).nickname,
            "date":dp.date,
            "inner":dp.inner,
            "goodNum":len(db.filter("good",plId=dp.id))
        })
    return {
        "message":"success",
        "pls":pls,
        "blog":{
            "title":blog.title,
            "inner":blog.inner,
            "id":blog.id,
            "user":db.get("user",id=blog.user).nickname,
            "date":blog.date,
            "tag":sortItems[blog.tag]
        }
    }
if __name__ == "__main__":
    uvicorn.run(app)
