import re
import structllm as sllm
import json
import openai

def Interview(args, data, character, names, descriptions, chunk_id):

    #args 系统设置
    #data：text ：访谈内容
    #character：访谈者编号
    #names :访谈者身份
    #description :访谈者介绍
    llm = sllm.llm.gpt(args)
    qa_data , cleaned_data = [], []
    summary_data = None
    context_data = data
    chunk_data = ''
    for i in range(len(data)):  
       mini_data = data[i]
       mini_character = character[i]
       max_retries = 3         # 最大重试次数
       retry_count = 0         # 当前重试次数
       total_num = 0           # 防止卡死
       result = None
       flag = True
       while (flag) :
           retry_count += 1
           #读取
           query_prompt = sllm.query_prompt.query_prompt(args, mini_data, mini_character, names, descriptions) #[配置文件 ,谈话内容 ，]
           ########1.清洗文本#######
           query_prompt.create_prompt(task = "clean")
           responses = llm.get_response(query_prompt.naive_prompt)
           
           for response in responses:
                try:
                    result = response.choices[0].message.content
                    result = result.strip('[]')
                    cleaned_data.append(names[character[i]-1]+":"+result+"\n")
                    """
                    print(names[character[i]-1]+" : "+result)
                    with open("/home/wcy/code/InterviewSystem-v0.1/output/test_data.txt", "a", encoding="utf-8") as file:
                         file.write(names[character[i]-1]+":"+result+"\n")
                    """
                except openai.BadRequestError as e: # 非法输入 '$.input' is invalid. query返回结果为：请输入详细信息等
                    print(e)
                    total_num += 1
                    continue

                except IndexError as e: # 得不到正确格式的query: set1=(fastest car)
                    print(e)
                    total_num += 1 # 防止卡死
                    continue

                except openai.APITimeoutError as e: # 超时
                    print(e)
                    total_num += 1 # 防止卡死
                    continue

                except ValueError as e: # maximum context length
                    print(e)
                    continue

                except Exception as e: # 其他错误
                    print(e)
                    total_num += 1 # 防止卡死
                    continue
                flag = False

    for i in range(len(cleaned_data)):
        chunk_data = chunk_data + cleaned_data[i]
    
    flag = True
    ns ,qs =[], []
    while (flag) :
        ########2.Extract Questions#######
        query_prompt = sllm.query_prompt.query_prompt(args, cleaned_data)
        query_prompt.create_prompt(task = "extract_q")
        responses_qs = llm.get_response(query_prompt.naive_prompt)

        for response_qs in responses_qs:
            try:
                #解析response_qa
                result = response_qs.choices[0].message.content
                ns,qs = sllm.align.get_parameters(result)
                #check if parameters size is same
            except openai.BadRequestError as e: # 非法输入 '$.input' is invalid. query返回结果为：请输入详细信息等
                print(e)
                total_num += 1
                continue

            except IndexError as e: # 得不到正确格式的query: set1=(fastest car)
                print(e)
                total_num += 1 # 防止卡死
                continue

            except openai.APITimeoutError as e: # 超时
                print(e)
                total_num += 1 # 防止卡死
                continue

            except ValueError as e: # maximum context length
                print(e)
                continue

            except Exception as e: # 其他错误
                print(e)
                total_num += 1 # 防止卡死
                continue
            flag = False
    ans = []
    for n ,q in zip(ns,qs):
        question = n+":"+q
        #import pdb; pdb.set_trace()
        flag = True
        while (flag) :
            ########3.Extract answers#######
            #extract QA pairs
            query_prompt = sllm.query_prompt.query_prompt(args, cleaned_data, character)
            query_prompt.create_prompt(task = "extract_a", question = question)
            responses_qa = llm.get_response(query_prompt.naive_prompt)
            for response_qa in responses_qa:
                try:
                    #解析response_qa
                    result = response_qa.choices[0].message.content
                    ans.append(result)
                except openai.BadRequestError as e: # 非法输入 '$.input' is invalid. query返回结果为：请输入详细信息等
                    print(e)
                    total_num += 1
                    continue

                except IndexError as e: # 得不到正确格式的query: set1=(fastest car)
                    print(e)
                    total_num += 1 # 防止卡死
                    continue

                except openai.APITimeoutError as e: # 超时
                    print(e)
                    total_num += 1 # 防止卡死
                    continue

                except ValueError as e: # maximum context length
                    print(e)
                    continue

                except Exception as e: # 其他错误
                    print(e)
                    total_num += 1 # 防止卡死
                    continue     
                flag = False
    
    qa_data = list(zip(ns,qs,ans))
    
    flag = True
    while (flag) :
        ########4.Extract summary#######
        query_prompt = sllm.query_prompt.query_prompt(args, cleaned_data, character, names, descriptions)
        query_prompt.create_prompt(task = "summary")
        responses_sum = llm.get_response(query_prompt.naive_prompt)
        for response_sum in responses_sum:
            try:
                #解析response_sum
                summary_data = response_sum.choices[0].message.content
                             
            except openai.BadRequestError as e: # 非法输入 '$.input' is invalid. query返回结果为：请输入详细信息等
                print(e)
                total_num += 1
                continue

            except IndexError as e: # 得不到正确格式的query: set1=(fastest car)
                print(e)
                total_num += 1 # 防止卡死
                continue

            except openai.APITimeoutError as e: # 超时
                print(e)
                total_num += 1 # 防止卡死
                continue

            except ValueError as e: # maximum context length
                print(e)
                continue

            except Exception as e: # 其他错误
                print(e)
                total_num += 1 # 防止卡死
                continue
            flag = False

    #import pdb; pdb.set_trace()
    ########3.注入数据库#######
    sllm.retrieve.get_qas_collection_and_write(args.encoder_model , qa_data = qa_data, chunk_id = chunk_id)
    sllm.retrieve.get_summary_collection_and_write(args.encoder_model , summarydata = summary_data, chunk_data = chunk_data, chunk_id = chunk_id)
    sllm.retrieve.get_context_collection_and_write(args.encoder_model , context_data = cleaned_data, chunk_id = chunk_id)
    
    return cleaned_data, qa_data, summary_data
