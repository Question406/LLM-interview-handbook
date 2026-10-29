---
id: afm-pipeline-mm-tool-use
kind: design
situation: 读图与界面操作都可能造成填表错误。
task: 采集对齐且可检查的 tool-use trajectories。
approach: 合成真值、动作前截图和导出文件核验。
result: 新布局有效，读图错与点击错分别补数据。
---

## 可以这样回答

我会选一个比较容易检查结果的任务，比如给 agent 一张票据截图，让它把日期、币种和总额填进表格，再导出文件。这样既要读图，也要实际操作软件，最后还有一个可以检查的结果。

最开始我会用合成票据。先确定日期和金额，再把它们渲染成不同样式的图片，所以我知道正确答案是什么。让 agent 在固定的软件环境里操作，记录它每一步看到的截图和接下来的动作。结束以后，我直接检查导出的表格，不能因为 agent 说“已经完成”就算成功。

如果金额填错了，我会先看它是把图读错了，还是知道金额却填错了格子。比如小计是115，总额是128.50，它填了115，这更像是字段理解的问题；如果它正确说出了128.50，却输入到日期那一格，问题就更接近界面操作。这两种错误，我会补不同的数据。

训练时先用实际完成、过程也合理的 trajectories。评价时换一批票据布局，而不只是换金额。如果换个排版就不会了，说明它可能记住了位置，没有真正学会找总额。这条 pipeline 是我会设计的扩展；和我参与的 VisualSkill 工作可以连接起来讲，但不能把这套票据实验说成已经做过。

## 被追问时再展开

**为什么不用 OCR 加脚本？** 我会把它作为 baseline。如果固定票据模板用 OCR 就能很好解决，那没有必要强行做复杂 agent。这个例子更适合需要理解变化的页面、再跨软件完成操作的场景。

**数据怎么扩大？** 我会根据真实失败补变化，比如小计和总额很接近、日期格式不同、表格需要滚动。先确认是哪一种变化带来错误，再生成对应的新样本，而不是只把同一个模板复制很多遍。

## 英文口述参考

I would use a task with an outcome I can check, such as reading a receipt image, entering the date and total into a spreadsheet, and exporting the file.

I would begin with synthetic receipts, so I know the correct fields before rendering the image. During collection, I would record the screenshot the agent saw before each action. Afterwards, I would inspect the exported spreadsheet. The agent saying it succeeded would not be enough.

If it failed, I would separate reading errors from action errors. Entering the subtotal instead of the total suggests a different data problem from reading the amount correctly but typing it into the wrong cell. I would collect examples for the failure I actually observed, and test on new receipt layouts to see whether the model learned more than a fixed screen position.
