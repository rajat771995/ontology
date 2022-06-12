# import json
# import pika
# import os
# import subprocess
# import sys
# import hashlib
# import time
# import logging
# import threading
# from functools import partial
# import functools
# from TPool.TPool import Pool
# # from threading import Lock
# from multiprocessing import Process, Pipe, Lock
# import multiprocessing
# import traceback
#
# def set_config(logger, logdir=""):
#     """
#     :param logger: logger
#     :param logdir: the directory log
#     :return:
#     """
#     if logdir != "":
#         handler = logging.FileHandler(logdir)
#     else:
#         handler = logging.StreamHandler()
#     formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
#     handler.setFormatter(formatter)
#     logger.addHandler(handler)
#     logger.setLevel(logging.DEBUG)
#     return logger
#
#
# queue_name = 'ontoology'
#
# print("Will check the rabbit host \n\n\n")
# if 'rabbit_host' in os.environ:
#     rabbit_host = os.environ['rabbit_host']
#     print("rabbit_host: "+rabbit_host)
# else:
#     rabbit_host = 'localhost'
#     print("rabbit_host: "+rabbit_host)
#
# if 'rabbit_log_dir' in os.environ:
#     log_dir = os.environ['rabbit_log_dir']
#     logger = multiprocessing.get_logger()
#     # logger = logging.getLogger(__name__)
#     logger = set_config(logger, log_dir)
# else:
#     # logger = logging.getLogger(__name__)
#     logger = multiprocessing.get_logger()
#     logger = set_config(logger)
#
#
# def run_rabbit():
#     """
#     Run the rabbit consumer
#     :return:
#     """
#     if 'rabbit_processes' in os.environ:
#         try:
#             num = int(os.environ['rabbit_processes'])
#             if 'virtual_env_dir' in os.environ:
#                 comm = "nohup %s %s %s %s" % (os.path.join(os.environ['virtual_env_dir'], 'bin', 'python'),
#                                               os.path.join(os.path.dirname(os.path.realpath(__file__)), 'rabbit.py'),
#                                               str(num), os.environ['setting_module'], ' &')
#             else:
#                 comm = "nohup python %s %s %s" % (
#                 os.path.join(os.path.dirname(os.path.realpath(__file__)), 'rabbit.py'), str(num),
#                 '&')
#             logger.debug("run_rabbit> comm: " + comm)
#             print("run_rabbit> comm: " + comm)
#             subprocess.Popen(comm, shell=True)
#         except:
#             logger.error('run_rabbit> The rabbit_processes is: <%s>' % str(os.environ['rabbit_processes']))
#     else:
#         logger.debug('run_rabbit> rabbit_processes is not in environ')
#
# # def send(message_json):
# #     """
# #     :param message:
# #     :return:
# #     """
# #     return direct_call(message_json)
#
# def send(message_json):
#     """
#     :param message:
#     :return:
#     """
#     global logger
#     connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host))
#     channel = connection.channel()
#     queue = channel.queue_declare(queue=queue_name, durable=True, auto_delete=False)
#     logger.debug("send> number of messages in the queue is: "+str(queue.method.message_count))
#     message = json.dumps(message_json)
#     logger.debug("send> sending message: "+str(message))
#     # logger.debug(message)
#     channel.basic_publish(exchange='',
#                           routing_key=queue_name,
#                           body=message,
#                           properties=pika.BasicProperties(
#                               delivery_mode=2,  # make message persistent
#                           ))
#     connection.close()
#     num = get_num_of_processes_of_rabbit()
#     if num < 1:
#         logger.warning("send> RESTART -- number of processes were: "+str(num))
#         run_rabbit()
#
#
# def get_pending_messages():
#     """
#     get number of pending messages
#     :return:
#     """
#     global logger
#     try:
#         connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host))
#     except:
#         msg = "exception 1 in connecting"
#         logger.debug(msg)
#         # print(msg)
#         time.sleep(3)
#         try:
#             connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host))
#         except:
#             logger.debug(msg+" for the second time")
#             return -1
#     channel = connection.channel()
#     queue = channel.queue_declare(queue=queue_name, durable=True, auto_delete=False)
#     num = queue.method.message_count
#     connection.close()
#     return num
#
#
# def get_num_of_processes_of_rabbit():
#     """
#     :return:
#     """
#     import os
#     out = os.popen('ps -ef | grep rabbit.py').read()
#     lines = out.split('\n')
#     one = False
#     for line in lines:
#         if 'python' in line and 'rabbit.py' in line:
#             print("line: ")
#             print(line)
#             p_tokens = line.split('rabbit.py')
#             if len(p_tokens) > 1:
#                 tokens = p_tokens[1].strip().split(' ')
#                 if tokens[0].strip().isdigit():
#                     return int(tokens[0].strip())
#                 else:
#                     print("ptokens: ")
#                     print(p_tokens)
#                     print("tokens: ")
#                     print(tokens)
#                     # return 1
#                     one = True
#     if one:
#         return 1
#     return -1
#
#
# def direct_call(j):
#     """
#     Consume messages from the ready queue
#     :param j:
#     :return:
#     """
#     global logger
#     try:
#         if j['action'] in ['magic', 'change_conf', 'publish']:
#             repo_name = j['repo']
#             logger.debug(" ---  Consuming: " + repo_name + "\n" + str(j))
#             if j['action'] == 'magic':
#                 logger.debug('starting a magic process')
#                 handle_action(j, logger)
#             elif j['action'] == 'change_conf':
#                 logger.debug('starting a config change process')
#                 handle_conf_change(j, logger)
#             elif j['action'] == 'publish':
#                 logger.debug('starting a publish process')
#                 handle_publish(j, logger)
#             else:
#                 logger.debug("starting nothing")
#             logger.debug(repo_name+" Completed!")
#             return True
#
#     except Exception as e:
#         print("ERROR: "+str(e))
#         print("Message: "+str(j))
#         logger.debug("dERROR: "+str(e))
#         logger.debug("dMessage: "+str(j))
#         logger.error("ERROR: "+str(e))
#         logger.error("Message: "+str(j))
#         return False
#
#
# def callback_consumer(lock, sender, receiver, logger, j):
#     # lock = extra['lock']
#     # logger = extra['logger']
#     # receiver = extra['receiver']
#     # sender = extra['sender']
#     repo_name = j['repo']
#     logger.debug(" ---  Consuming: " + repo_name + "\n" + str(j))
#     if j['action'] == 'magic':
#         logger.debug('starting a magic process')
#         handle_action(j, logger)
#     elif j['action'] == 'change_conf':
#         logger.debug('starting a config change process')
#         handle_conf_change(j, logger)
#     elif j['action'] == 'publish':
#         logger.debug('starting a publish process')
#         handle_publish(j, logger)
#     else:
#         logger.debug("starting nothing")
#     logger.debug(repo_name + " Completed!")
#     lock.acquire()
#     locked_repos = receiver.recv()
#     logger.debug(repo_name + " to remove it from locked repos")
#     locked_repos.remove(repo_name)
#     logger.debug(repo_name + " is removed")
#     logger.debug("locked repos: ")
#     logger.debug(str(locked_repos))
#     sender.send(locked_repos)
#     lock.release()
#     logger.debug("")
#
#
# def callback2(extra, ch, method, properties, body):
#     """
#     Consume messages from the ready queue
#     :param extra:
#     :param ch:
#     :param method:
#     :param properties:
#     :param body:
#     :return:
#     """
#
#     lock = extra['lock']
#     logger = extra['logger']
#     receiver = extra['receiver']
#     sender = extra['sender']
#
#     try:
#         j = json.loads(body)
#         if j['action'] in ['magic', 'change_conf', 'publish']:
#             repo_name = j['repo']
#             #logger.debug('callback repo: '+repo_name)
#             lock.acquire()
#             locked_repos = receiver.recv()
#             busy = repo_name in locked_repos
#             if not busy:
#                 repo_pure_name = repo_name.split('/')[1]
#                 pure_locked = [r.split('/')[1] for r in locked_repos]
#                 pure_busy = repo_pure_name in pure_locked
#             else:
#                 pure_busy = busy
#             if not pure_busy:
#                 logger.debug('not busy repo: ' + repo_name + " (" + str(method.delivery_tag) + ")")
#                 locked_repos.append(repo_name)
#                 logger.debug("start locked repos: "+str(locked_repos))
#             else:
#                 logger.debug('is busy repo: ' + repo_name + " (" + str(method.delivery_tag) + ")")
#                 #logger.debug("busy ones: "+str(locked_repos))
#             sender.send(locked_repos)
#             lock.release()
#             if busy:
#                 #logger.debug(repo_name+" is busy --- ")
#                 time.sleep(5)
#                 ch.basic_nack(delivery_tag=method.delivery_tag, multiple=False, requeue=True)
#             else:
#                 p = Process(target=callback_consumer, args=(lock, sender, receiver, logger, j))
#                 p.start()
#                 ch.basic_ack(delivery_tag=method.delivery_tag)
#
#                 # logger.debug(" ---  Consuming: " + repo_name + "\n" + str(body))
#                 # # logger.debug(body)
#                 # if j['action'] == 'magic':
#                 #     logger.debug('starting a magic process')
#                 #     # p = Process(target=handle_action, args=(j, logger))
#                 #     # p.start()
#                 #     # p.join()
#                 #     handle_action(j, logger)
#                 # elif j['action'] == 'change_conf':
#                 #     logger.debug('starting a config change process')
#                 #     # p = Process(target=handle_conf_change, args=(j, logger))
#                 #     # p.start()
#                 #     # p.join()
#                 #     handle_conf_change(j, logger)
#                 # elif j['action'] == 'publish':
#                 #     logger.debug('starting a publish process')
#                 #     # p = Process(target=handle_publish, args=(j, logger))
#                 #     # p.start()
#                 #     # p.join()
#                 #     handle_publish(j, logger)
#                 # else:
#                 #     logger.debug("starting nothing")
#                 # logger.debug(repo_name+" Completed!")
#                 # lock.acquire()
#                 # locked_repos = receiver.recv()
#                 # logger.debug(repo_name+" to remove it from locked repos")
#                 # locked_repos.remove(repo_name)
#                 # logger.debug(repo_name+" is removed")
#                 # logger.debug("locked repos: ")
#                 # logger.debug(str(locked_repos))
#                 # sender.send(locked_repos)
#                 # lock.release()
#                 # logger.debug(repo_name+" is sending the ack")
#                 # ch.basic_ack(delivery_tag=method.delivery_tag)
#
#     except Exception as e:
#         print("ERROR: "+str(e))
#         print("Message: "+str(body))
#         logger.debug("dERROR: "+str(e))
#         logger.debug("dMessage: "+str(body))
#         logger.error("ERROR: "+str(e))
#         logger.error("Message: "+str(body))
#
#
# def handle_publish(j, logger):
#     """
#     :param j:
#     :param logger: logger
#     :return:
#     """
#     try:
#         logger.debug("try publish")
#         try:
#             import autoncore
#             autoncore.django_setup_script()
#         except:
#             from OnToology import autoncore
#         print("set logger")
#         logger.debug('handle_publish> going for previsual')
#         try:
#             err, orun = autoncore.previsual(useremail=j['useremail'], target_repo=j['repo'], branch=j['branch'])
#             logger.debug("handle_publish> prev error: %s" % str(err))
#         except Exception as e:
#             logger.debug('handle_publish> Error in previsualisation')
#             logger.error('handle_publish> ERROR in previsualisation: '+str(e))
#             return
#         if err.strip() != "":
#             logger.debug('handle_publish> Error in previsual and will stop')
#             return
#         logger.debug('handle_publish> going for publish')
#         try:
#             autoncore.publish(name=j['name'], target_repo=j['repo'], ontology_rel_path=j['ontology_rel_path'],
#                               useremail=j['useremail'], branch=j['branch'], orun=orun)
#         except Exception as e:
#             traceback.print_exc()
#             logger.error('handle_publish> ERROR in publication: '+str(e))
#             return
#         logger.debug('handle_publish> done')
#     except Exception as e:
#         err = "Error in handle_publish"
#         print(err)
#         logger.debug(err)
#         logger.error(err)
#         err = str(e)
#         print(err)
#         logger.debug(err)
#         logger.error(err)
#
#
# def handle_action(j, logger, raise_exp=False):
#     """
#     :param j:
#     :return:
#     """
#     try:
#         logger.debug("try action")
#         try:
#             import autoncore
#             autoncore.django_setup_script()
#         except:
#             from OnToology import autoncore
#
#         print("set logger")
#         logger.debug("handle_action> ")
#         repo = j['repo']
#         if j['action'] == 'magic':
#             logger.debug("going for magic: "+str(j))
#             try:
#                 autoncore.git_magic(j['repo'], j['useremail'], j['changedfiles'], j['branch'], raise_exp=raise_exp)
#                 logger.debug("magic success")
#             except Exception as e:
#                 logger.debug("dException in magic")
#                 logger.debug("dException in magic for repo: "+j['repo'])
#                 logger.debug(str(e))
#                 logger.error("Exception in magic for repo: "+j['repo'])
#                 logger.error(str(e))
#                 print("Exception in magic for repo: "+j['repo'])
#                 print(str(e))
#                 traceback.print_exc()
#                 if raise_exp:
#                     raise Exception(str(e))
#             logger.debug("magic is done")
#         else:
#             logger.debug("dInvalid magic redirect: ")
#             logger.debug("dInvalid magic redirect with j: "+str(j))
#             logger.error("Invalid magic redirect: ")
#             logger.error("Invalid magic redirect with j: "+str(j))
#     except Exception as e:
#         logger.debug("dException 2 ")
#         logger.debug("dException 2 for magic: "+str(e))
#         logger.debug("dException for j: "+str(j))
#         logger.error("Exception 2 ")
#         logger.error("Exception 2 for magic: "+str(e))
#         logger.error("Exception for j: "+str(j))
#         traceback.print_exc()
#         if raise_exp:
#             raise Exception(str(e))
#     logger.debug("finished handle_action: "+str(j))
#
#
# def handle_conf_change(j, logger):
#     """
#     :param j:
#     :param logger: logger
#     :return:
#     """
#     try:
#         logger.debug("try change")
#         try:
#             import autoncore
#             autoncore.django_setup_script()
#         except:
#             from OnToology import autoncore
#         print("set logger")
#         logger.debug("handle_conf_change> ")
#         data = j['data']
#         if j['action'] == 'change_conf':
#             autoncore.change_configuration(user_email=j['useremail'],
#                                            target_repo=j['repo'], data=data, ontologies=j['ontologies'])
#             logger.debug("handle_conf_change> configuration is changed: "+str(j))
#         else:
#             logger.debug("handle_conf_change> invalid action: "+str(j))
#     except Exception as e:
#         err = "Error in handle_conf_change"
#         print(err)
#         logger.debug(err)
#         logger.error(err)
#         err = str(e)
#         print(err)
#         logger.debug(err)
#         logger.error(err)
#
#     logger.debug("finished handle_conf_change: "+str(j))
#
#
# def ack_message(channel, delivery_tag):
#     """Note that `channel` must be the same pika channel instance via which
#     the message being ACKed was retrieved (AMQP protocol constraint).
#     """
#     global logger
#     if channel.is_open:
#         channel.basic_ack(delivery_tag)
#         logger.debug("Channel is acked!")
#     else:
#         # Channel is already closed, so we can't ACK this message;
#         # log and/or do something that makes sense for your app in this case.
#         logger.debug("Channel is closed!")
#
#
# def start_pool(num_of_processes=1):
#     """
#     :param num_of_processes:
#     :return:
#     """
#     global logger
#     processes = []
#     lock = Lock()
#     sender, receiver = Pipe()
#     sender.send([])
#     for i in range(num_of_processes):
#         th = Process(target=single_worker, args=(i, lock, sender, receiver, logger))
#         th.start()
#         logger.debug("spawn: "+str(i))
#         processes.append(th)
#     logger.debug("total spawned: "+str(processes))
#     for idx, th in enumerate(processes):
#         th.join()
#         logger.info("Process is closed: "+str(idx))
#     logger.error("ALL ARE CONSUMED ..")
#
#
# def single_worker(worker_id, lock, sender, receiver, logger):
#     """
#     :param worker_id:
#     :return:
#     """
#     logger.debug('worker_id: '+str(worker_id))
#     # heartbeat=0 disable timeout
#     # heartbeat= 60 * 60 * 3 (3 hours)
#     # connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host, heartbeat=0))
#     worker_connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host))
#     channel = worker_connection.channel()
#     queue = channel.queue_declare(queue=queue_name, durable=True, auto_delete=False)
#     channel.basic_qos(prefetch_count=1)
#
#     abc = {
#             'lock': lock,
#             'sender': sender,
#             'receiver': receiver,
#             'logger': logger
#     }
#     abc_callback = partial(callback2, abc)
#     channel.basic_consume(queue=queue_name, on_message_callback=abc_callback)
#     print("Rabbit consuming is started ... "+str(worker_id))
#     logger.debug("Setting the logger ..."+str(worker_id))
#     logger.debug("test connection ..."+str(channel.is_open))
#     logger.debug("single_worker> number of messages in the queue is: " + str(queue.method.message_count))
#     channel.start_consuming()
#     logger.debug("single_worker> completed worker")
#
#
# if __name__ == '__main__':
#     print("In rabbit\n\n")
#     if len(sys.argv) > 1:
#         start_pool(int(sys.argv[1]))
#         if len(sys.argv) > 2:
#             from .djangoperpmodfunc import load
#             load(sys.argv[2])
#             import autoncore
#             from .localwsgi import *
#             print("\n\nrabbit __main__: .........................environ:")
#             print(environ)
#     else:
#         start_pool()
#
