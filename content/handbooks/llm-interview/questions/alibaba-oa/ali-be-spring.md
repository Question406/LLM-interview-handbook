---
id: ali-be-spring
section: alibaba-oa
order: 53
level: B
title: 阿里研发面：Spring Bean 生命周期和 AOP 怎么答？
quick: >-
  生命周期抓四段：实例化 → 填充属性 → 初始化（Aware → `BeanPostProcessor` → `@PostConstruct` / `InitializingBean`）→ 销毁回调，AOP 代理通常在初始化之后包上。代理有接口走 JDK 动态代理、没接口走 CGLIB 子类；类内部 `this.foo()` 自调用不经过代理，切面和事务都不生效。
tags:
  - Alibaba
  - Spring
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阿里校招 Java 面经（秒杀/LRU）
    url: https://www.nowcoder.com/feed/main/detail/0a3142d863914f689cc76fbc3bb68ba6
    type: candidate-first-hand
---

Bean 的生命周期我只讲四段：实例化、填充属性、初始化、销毁，AOP 代理一般在初始化的最后一步包上去，二十步清单不用背。AOP 最常考的是它的限制：只有经过代理对象的外部调用才会进切面，类内部 `this.foo()` 是直接调目标对象，切面和事务都不生效。这是阿里校招 Java 面的题。

Spring Bean 是容器管理的对象，容器负责创建、注入依赖、调用初始化，关闭时销毁。第一段实例化，用无参构造或工厂方法创建一个还没注入依赖的对象。第二段填充属性，按 `@Autowired` / `@Resource` / setter 注入依赖。第三段初始化：先走各种 `Aware`，让 Bean 拿到 `BeanName`、`ApplicationContext`；然后进 `BeanPostProcessor` 的 `postProcessBeforeInitialization`；接着是 `@PostConstruct`、`InitializingBean.afterPropertiesSet`、自定义 `init-method`；最后是 `postProcessAfterInitialization`，AOP 代理通常就在这里包一层。第四段销毁：`@PreDestroy`、`DisposableBean`、`destroy-method`。

| 阶段 | 你会碰到的回调 | 面试用来干什么 |
| --- | --- | --- |
| 实例化 | 构造器 | 构造器注入、构造器循环依赖 |
| 填充 | `@Autowired` | 依赖是否已可用 |
| 初始化前 / 后 | `BeanPostProcessor` | 代理、打点、校验 |
| 初始化 | `@PostConstruct` | 预热缓存、订阅 MQ |
| 销毁 | `@PreDestroy` | 停线程池、关连接 |

作用域默认是单例，全容器一份。`prototype` 每次获取都新建，但注入到单例里只会注入一次，要用 `ObjectFactory` 或 `@Lookup`；原型 Bean 的销毁容器不管，调用方要自己清理，否则容易漏连接。循环依赖靠三级缓存，把早期引用暴露出去，支持 setter 或字段注入里的循环依赖。构造器循环解不开，因为构造还没返回，对象还没创建完，早期引用无从谈起。AOP 和事务叠在循环依赖上会更绕，早期引用可能还不是最终的代理，面试说到「可能拿到半成品代理」就够了。

AOP 是把日志、鉴权、事务、限流这些横切逻辑从业务方法里拆出去，用代理在方法调用前后织入通知。Spring 默认有接口走 JDK 动态代理，没接口走 CGLIB 子类。通知类型有 before / after / around / after-returning / after-throwing，切点用表达式选方法。

事务 `@Transactional` 是 AOP 的特例。默认只回滚 RuntimeException；自调用不开启事务；方法必须是 `public`，并且从另一个 Bean 调进来。异常被吞、数据源不归 Spring 管理，事务也会失效。传播行为里校招常考 `REQUIRED`（加入当前事务）和 `REQUIRES_NEW`（挂起当前事务、开一个新的，适合「主单失败也要记审计」）。

## 放到阿里的场景里

比如下单服务里 `OrderService.placeOrder()` 标了 `@Transactional`，里面先写订单，再 `this.deductCoupon()`。优惠扣减上的事务或锁切面不会走，大促一压就会出现「订单写了、券没扣」或者反过来。改法是把扣券抽到独立的 Bean，或者注入自己的代理再调。初始化阶段也别在 `@PostConstruct` 里同步拉全量商品库，启动会被拖死；改成异步预热，并用就绪探针挡住流量。

配置中心、HSF / Dubbo 消费者这类 Bean，销毁时必须先摘流量再关线程池，否则发布过程中还有请求打到半关闭的池上。阿里内部发布常见的「先下线注册中心，再停 JVM」，对应的就是销毁顺序。循环依赖的真实案例：`PriceService` 依赖 `PromotionService`，后者又回调算价，字段注入能跑，但单测和阅读成本都高。能运行不代表设计合理，尽量用事件或第三方协调组件把循环拆开。

## 追问

**JDK 代理和 CGLIB 哪个能拦 `final` 方法？**
都拦不好。JDK 只拦接口方法，CGLIB 没法有效地子类化 `final` 类或方法。

**怎么让自调用也走事务？**
自注入代理、用 `AopContext.currentProxy()`，或者拆成两个 Bean。

**`BeanFactory` 和 `ApplicationContext` 差在哪？**
后者多了事件、国际化和 AOP 集成，日常用的都是后者。

**`@PostConstruct` 和 `afterPropertiesSet` 谁先执行？**
`@PostConstruct` 先。
