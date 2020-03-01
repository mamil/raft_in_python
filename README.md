# raft_in_python

## step by step

## fix getted_vote count error and add log

1. getted_vote需要在选举超期时归零

2. 增加log，记录vote信息

## Adding constraints to voting

1. 将心跳调整为3s，那么socket超时变为2s，选举超时也变为2s，直觉上会更随机一点-_-

2. [TODO] 增加了新的变量votedForTerm，很糟糕。

    因为在第一轮选举平票的时候，candidate会触发第2轮选举，但是这个时候，follower怎么知道是第二轮呢？

    不知道的话，就不能按照先来先得的原则投票了，像论文说的，会投给原先的那个candidateId，如果所有follower都这样，那不是又平票了？

        If votedFor is null or candidateId, and candidate’s log is at
        least as up-to-date as receiver’s log, grant vote

    所以先加了votedForTerm这个变量，来记录上次投的term，如果有更新的来，就投给更新的。

    但是这样又有问题了，一轮中会不会产生多次投票？或者说，RAFT中的一轮投票是怎么定义的呢？

    比如candidate1 发起term5的投票，follower1投一票，然后candidate2 发起term6的投票，follower1应该投吗？

    投的话是不是投了2票？不投的话如果是下一轮candidate2先到呢？感觉思路不对，还要多读读论文。

3. 删除了之前的sleep(),上次忘记了。

## commit 6968322ac59223a2c50b3b279d83b84ca3a094a7

1. 增加了已经获得的投票数，用于判断是否达到大多数。

    [TODO] 其实RAFT中的“大多数”，一直有点疑问，要大于一半吗？

2. 增加request_vote_response()函数，用来返回结果，后续的各种判断也放在这里。

3. 在票数大于一半时才从candidate转到leader。角色转换时清空票数。

4. node增加到5个。

## commit 933033c139a7dd95151c88075059863faed9cbc4

1. 增加了选举超时时间

2. 网络超时时间变为心跳超时-1， 主要避免网络延迟造成的超时

3. 在消息中加了type，id，便于识别信息。

4. 增加了3个角色的处理函数，实现还是比较简单的状态。

    ```python
    follower_handle() #没收到数据时，会比较是否超时了，收到则只处理数据。漏洞还是比较多的。
    leader_handle() #只发送AppendEntries，来维持统治
    candidate_handle() #收到数据时判断，进行状态变更，这只要收到True就直接变成leader。当然，这个实现是错误的。
    ```

5. [TODO] 用固定的receive超时充当timer的问题就比较明显了，RAFT中在leader消息超时之后，会随机(150,300)ms,然后转换到candidate状态，避免选票瓜分，其实这里要2个timer。一个是心跳，另一个是随机时间。现在会有瓜分选票的危险，后续解决

## commit c75fc98a9ab410474ef196ddc9b677dd80c32f22

1. 添加了论文中定义的一些属性，添加了request_vote()函数，实现还比较简单，只是向所有的node发请求。

## commit 32b26572ee155794ea85a11402f84d39cc9e9554

1. 完成了socket通信相关的东西

    self.serverSocket.settimeout(2)

    这里的server接收超时是为了防止一直卡在接收那里，阻碍整个流程。

2. [TODO] 这个地方没有仔细看接口实现，不太确定，是否会卡住

    self.send("from {}".format(self.id), self.peers[0]) #这里也需要考虑超时吗？？双端都是send会卡住？
