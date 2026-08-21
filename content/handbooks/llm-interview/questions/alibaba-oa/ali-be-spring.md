---
id: ali-be-spring
section: alibaba-oa
order: 53
level: B
title: 阿里研发面：Spring Bean 生命周期和 AOP 怎么答？
quick: >-
  实例化 → 填充属性 → Aware → `BeanPostProcessor` → 初始化（`@PostConstruct` / `InitializingBean`）→ 销毁回调。AOP 默认 JDK 接口代理或 CGLIB 子类。
tags:
  - Alibaba
  - Spring
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-18
sources:
  - title: 阿里校招 Java 面经（秒杀/LRU）
    url: https://www.nowcoder.com/feed/main/detail/0a3142d863914f689cc76fbc3bb68ba6
    type: candidate-first-hand
---

## 真题记录

- 岗位：阿里校招 Java

## 定义

Spring Bean 是容器管理的对象：容器负责创建、注入依赖、调用初始化、在关闭时销毁。生命周期口述抓四段，不要背二十步清单。第一段**实例化**，无参构造或工厂方法 new 出裸对象。第二段**填充属性**，按 `@Autowired` / `@Resource` / setter 把依赖灌进去。第三段**初始化**：先走各种 `Aware`（让 Bean 拿到 `BeanName`、`ApplicationContext`），再进入 `BeanPostProcessor` 的 `postProcessBeforeInitialization`，然后是 `@PostConstruct`、`InitializingBean.afterPropertiesSet`、自定义 `init-method`，最后 `postProcessAfterInitialization`——AOP 代理通常在这里包一层。第四段**销毁**：`@PreDestroy`、`DisposableBean`、`destroy-method`。

AOP 的定义是：把横切逻辑（日志、鉴权、事务、限流）从业务方法里拆出去，用代理在方法调用前后织入通知。Spring 默认：有接口走 JDK 动态代理，没接口走 CGLIB 子类。通知类型是 before / after / around / after-returning / after-throwing。切点用表达式选方法。核心限制一句话：**只有经过代理对象的外部调用才会进切面**，`this.foo()` 是直接调目标对象，切面和事务都不生效。

## 对比 / 分层

| 阶段 | 你会碰到的回调 | 面试用来干什么 |
| --- | --- | --- |
| 实例化 | 构造器 | 构造器注入、构造器循环依赖 |
| 填充 | `@Autowired` | 依赖是否已可用 |
| 初始化前 / 后 | `BeanPostProcessor` | 代理、打点、校验 |
| 初始化 | `@PostConstruct` | 预热缓存、订阅 MQ |
| 销毁 | `@PreDestroy` | 停线程池、关连接 |

作用域：默认单例，全容器一份；`prototype` 每次要都新建，但注入到单例里只会注入一次，需要 `ObjectFactory` 或 `@Lookup`。循环依赖：单例用三级缓存，把早期引用暴露出去，让 setter / 字段注入的环能转起来；**构造器循环解不开**，因为对象还没创建完。AOP 和事务叠在循环依赖上会更绕：早期引用可能还不是最终代理，面试说到「可能拿到半成品代理」就够。

事务 `@Transactional` 是 AOP 的特例。默认只回滚 RuntimeException；自调用不开启事务；方法必须是 `public` 且从另一个 Bean 进来。传播行为里校招常考 `REQUIRED`（加入当前事务）和 `REQUIRES_NEW`（挂起后开新事务，适合「主单失败也要记审计」）。

## 阿里场景

下单服务里 `OrderService.placeOrder()` 标了 `@Transactional`，里面先写订单再 `this.deductCoupon()`。优惠扣减上的事务或锁切面不会走，大促一压就会出现「订单写了、券没扣」或反过来。改法是把扣券抽到独立 Bean，或注入自己的代理再调。初始化阶段也不要在 `@PostConstruct` 里同步拉全量商品库，启动会被拖死；改成异步预热，并用就绪探针挡住流量。

配置中心、HSF / Dubbo 消费者这类 Bean，销毁时必须先摘流量再关线程池，否则发布过程中还有请求打到半关闭的池。阿里内部发布常见「先下线注册中心，再停 JVM」，对应的就是销毁顺序。循环依赖的真实案例：`PriceService` 依赖 `PromotionService`，后者又回调算价，字段注入能跑，但单测和阅读成本高，校招更加分的说法是「能转不等于设计对，尽量拆成事件或第三方面」。

## 追问

- 为什么构造器循环依赖三级缓存救不了？构造还没返回，早期引用无从谈起。
- JDK 代理和 CGLIB 哪个能拦 `final` 方法？都不能很好地拦：JDK 只拦接口方法，CGLIB 不能有效子类化 `final` 类 / 方法。
- 如何让自调用也走事务？自注入代理、`AopContext.currentProxy()`，或拆 Bean。
- `BeanFactory` 和 `ApplicationContext` 差在哪？后者多了事件、国际化、AOP 集成，日常用后者。
- `@PostConstruct` 和 `afterPropertiesSet` 谁先？`@PostConstruct` 先。
- 原型 Bean 的销毁谁负责？容器不管，调用方自己清，否则容易漏连接。
- 事务失效还有哪些？异常被吞、方法不是 public、数据源不是 Spring 管理的。
