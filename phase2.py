from pymongo import MongoClient
import json
from datetime import datetime


""" (1) the number of questions owned and the average score for those questions, 
(2) the number of answers owned and the average score for those answers, and 
(3) the number of votes registered for the user.
"""



def show_user_info(posts, votes, ownerUserId):
    NumQuestions=0
    info_1 = posts.aggregate([
        {"$match":{"OwnerUserId" : ownerUserId, "PostTypeId" : "1"}},
        {"$group" :  
            {"_id" : "$OwnerUserId",
            "NumQuestions": {"$sum" : 1},
            "AvgScore" : {"$avg" : "$Score"}
            }
        }
    ])
    print(list(info_1))

    info_2 = posts.aggregate([
        {"$match":{"OwnerUserId" : ownerUserId, "PostTypeId" : "2"}},
        {"$group" :  
            {"_id" : "$OwnerUserId",
            "NumAnswers": {"$sum" : 1},
            "AvgScore" : {"$avg" : "$Score"}
            }
        }
    ])

    print(list(info_2))

    info_3 = votes.aggregate([
        {"$match":{"UserId" : ownerUserId}},
        {"$group" :  
            {"_id" : "$UserId",
            "NumVotes": {"$sum" : 1}
            }
        }
    ])
    print(list(info_3))
    return

"""Rules: Post a question. 
The user should be able to post a question by *providing a *title text, a *body text, and *zero or more tags.
The post should be properly recorded in the database. A *unique id should be assigned to the post by your system, 
the *post type id should be set to 1 (to indicate that the post is a question), 
the post *creation date should be set to the current date and the *owner user id should be set to the user posting it 
(if a user id is provided). The quantities Score, ViewCount, AnswerCount, CommentCount, 
and FavoriteCount are all set to zero and the *content license is set to "CC BY-SA 2.5".
"""


def post_a_question(posts,ownerid):
    title = input("Please enter title for your question: ")
    body = input("Please enter body for your question: ")
    print("Please enter tags for your question")
    tags = input("(please enter tags within < > ; press 0 if no tag): ")
    date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    max_id = posts.find_one(sort=[("Id", -1)])
    uniqID = str(int(max_id["Id"])+1)

    newQuestion = {
        "Id":uniqID,
        "PostTypeId": "1",
        "AcceptedAnswerId": "None",
        "CreationDate": date,
        "Score": 0,
        "ViewCount": 0,
        "Body": body,
        "OwnerUserId": ownerid,
        "LastEditorUserId": ownerid,
        "LastEditDate": date,
        "LastActivityDate": date,
        "Title": title,
        "Tags": tags,
        "AnswerCount": 0,
        "CommentCount": 0,
        "FavoriteCount": 0,
        "ContentLicense": "CC BY-SA 2.5"
    }
    posts.insert_one(newQuestion)

# Search for questions and display the result.
def search_for_questions(posts):
    print("Enter the keywords seperated by | to search:")
    regex = input();
    result = posts.find(
        { 
            "PostTypeId" : "1",
            "$or":[
                {"Title": {"$regex": regex,"$options" : "i"}},
                {"Body": {"$regex": regex,"$options" : "i"}},
                {"Tags": {"$regex": regex,"$options" : "i"}}
            ]    
        },
        {
            "Title" : 1,
            "CreationDate" : 1,
            "Score" : 1,
            "AnswerCount" : 1,
            "Id" : 1,
            "_id" : 0
            
        }
    )

    for r in result:
        print(r)

    print("Enter the ID from the listed post to select")
    postID = input()
    full_info = posts.find({"Id":postID},{"_id" : 0})
    for i in full_info:
        for j in i:
            print(j,i[j])
    posts.update_one({"Id":postID},{"$inc":{"ViewCount":1}})
    return postID


#Answer the selected question
def Question_action_Answer(posts,postID,usrID):
    print("Please provide a text to answer the selected question.")
    usrText = input()
    max_id = posts.find_one(sort=[("Id", -1)])
    uniqID = str(int(max_id["Id"])+1)
    date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    newAnswer = {
        "Id":uniqID,
        "ParentId":postID,
        "PostTypeId": "2",
        "CreationDate": date,
        "Score": 0,
        "ViewCount": 0,
        "Body": usrText,
        "OwnerUserId": usrID,
        "CommentCount": 0,
        "FavoriteCount": 0,
        "ContentLicense": "CC BY-SA 2.5"
    }
    posts.insert_one(newAnswer)





#List the answer of selected question with the accepted answer on the top with a star
def List_Answers(posts,postID):
    acptAnswerIDList = posts.find({"Id":postID},{"_id" : 0,"AcceptedAnswerId":1})
    List = acptAnswerIDList
    acptAnswerID = None
    if list(List):
        for a in acptAnswerIDList:
            acptAnswerID = a["AcceptedAnswerId"]
        acptAnswer = posts.find(
            {
                    "Id" : acptAnswerID
                },
                {
                    "Body": { "$substr" : [ "$Body", 0, 70]},
                    "CreationDate" : 1,
                    "Score" : 1,
                    "Id" : 1,
                    "_id" : 0
                }
            )
        print("*", end = '')
        for a in acptAnswer:
            print(a)
    othAnswers = posts.find(
        {"$and": [
            {"ParentId" : postID},
            {"Id" :{"$ne":acptAnswerID}}
            ]
        },
        {
            "Body": { "$substr" : [ "$Body", 0, 70]},
            "CreationDate" : 1,
            "Score" : 1,
            "Id" : 1,
            "_id" : 0
        }
        )
    for o in othAnswers:
        print(o)
    print("please type the Id number to select")
    answerId = input()
    full_info = posts.find({"Id":answerId},{"_id" : 0})
    for i in full_info:
        for j in i:
            print(j,i[j])
    return answerId

#Vote an answer or a question, the same user cannot vote twice on the same post.
def action_Vote(posts,votes,postID,userID):
    date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    max_id = votes.find_one(sort=[("Id", -1)])
    uniqID = str(int(max_id["Id"])+1)
    if userID: 
        isVoted = votes.find(
            {
                "PostId" : postID,
                "UserId" : userID
            },
            {
                "_id" : 0
            }
        )
        if list(isVoted):
            print("User has already voted on the same post")
        else:
            userVote={
                "Id" : uniqID,
                "PostId" : postID,
                "VoteTypeId" : "2",
                "UserId" : userID,
                "CreationDate": date
            }
            votes.insert_one(userVote)
            posts.update_one({"Id":postID},{"$inc":{"Score":1}})
            print("Voted!")
    else:
        userVote={
            "Id" : uniqID,
            "PostId" : postID,
            "VoteTyoeID": "2",
            "CreationDate" : date
        }
        votes.insert_one(userVote)
        posts.update_one({"Id":postID},{"$inc":{"Score":1}})
        print("Voted!")
    return




def main():
    user = MongoClient()
    db = user["291db"]

    # collist = db.list_collection_names()
    # if ("posts_collection" in collist or "tags_collection" in collist or "votes_collection" in collist):
    #     print("The collection exist")

    posts_collection = db["posts_collection"]
    tags_collection = db["tags_collection"]
    votes_collection = db["votes_collection"]
    quit=False
    back=False
    while(not quit):
        print("please enter the numerical user id if you wish: ")
        owner = input("Would you like to provide your owner id? (y/n): ")
        if owner=="y":
            usrID = input("Please enter you owner id: ")
            show_user_info(posts_collection,votes_collection,usrID) 
        elif owner=='quit':
            break
        else:
            usrID = None
        while(not back):
            print("please choose from the following to proceed:")
            print("\t Press '1' and 'Enter' to Post a question")
            print("\t Press '2' and 'Enter' to Search for questions")
            # ... add what ever action you need to put here
            usrInput = input()
            if usrInput == '1':
                post_a_question(posts_collection,usrID)
            elif usrInput == '2':
                postID=search_for_questions(posts_collection)
                if postID == 'back':
                    break
                elif postID == 'quit':
                    quit==True
                    break
                else:
                    while(True):
                        print("\t Press '1' and 'Enter' to answer the selected question")
                        print("\t Press '2' and 'Enter' to list and select the selected")
                        print("\t Press '3' and 'Enter' to vote a question")
                        usrOpt = input()
                        if usrOpt == '1':
                            Question_action_Answer(posts_collection,postID,usrID)
                        elif usrOpt == '2':
                            AnswerID = List_Answers(posts_collection,postID)
                            if AnswerID == 'back':
                                break
                            elif AnswerID == 'quit':
                                quit=True
                                back=True
                                break
                            else:
                                print("\t Press '1' and 'Enter' to vote an Answer")
                                usrOpt = input()
                                if usrOpt == '1':
                                    action_Vote(posts_collection,votes_collection,AnswerID,usrID)
                                elif usrOpt == 'quit':
                                    quit = True
                                    back = True
                                    break
                                elif usrOpt == 'back':
                                    break
                        elif usrOpt == '3':
                            action_Vote(posts_collection,votes_collection,postID,usrID)
                        elif usrOpt == 'quit':
                            quit = True
                            back = True
                            break
                        elif usrOpt == 'back':
                            break
            elif usrInput == 'back':
                break
            elif usrInput == 'quit':
                quit = True
                break




if __name__ == "__main__":
    main()

