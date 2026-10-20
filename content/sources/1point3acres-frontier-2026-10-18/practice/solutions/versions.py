def resolve(repo, roots):
    """为根需求及其全部传递依赖选出一组一致的版本，无解时返回 None。

    repo[package][version] 是这个版本的依赖：{依赖包: 允许的版本集合}。
    roots 是 {包: 允许的版本集合}。返回 {包: 选中的版本}。
    """

    def search(chosen, allowed):
        # 已选的版本必须仍满足所有约束（新加的依赖可能收紧了它）
        for package, version in chosen.items():
            if version not in allowed[package]:
                return None
        pending = [package for package in allowed if package not in chosen]
        if not pending:
            return chosen

        candidates = {
            package: sorted(set(repo.get(package, {})) & allowed[package])
            for package in pending
        }
        # 先处理候选最少的包（MRV），冲突能更早暴露
        package = min(pending, key=lambda name: (len(candidates[name]), name))
        for version in candidates[package]:
            next_allowed = narrow(allowed, repo[package][version])
            if next_allowed is None:
                continue
            answer = search({**chosen, package: version}, next_allowed)
            if answer is not None:
                return answer
        return None

    def narrow(allowed, dependencies):
        """把一个版本的依赖并入约束；某个包没有可选版本时返回 None。"""
        next_allowed = {package: set(versions) for package, versions in allowed.items()}
        for dependency, versions in dependencies.items():
            current = next_allowed.get(dependency, set(repo.get(dependency, {})))
            next_allowed[dependency] = current & set(versions)
        if any(not versions for versions in next_allowed.values()):
            return None
        return next_allowed

    initial = {package: set(versions) for package, versions in roots.items()}
    return search({}, initial)


def test():
    repo = {
        "A": {1: {"B": {1}}, 2: {"B": {2}}},
        "B": {1: {}, 2: {}},
    }

    # A1 依赖 B1，与根要求的 B1 一致
    assert resolve(repo, {"A": {1, 2}, "B": {1}}) == {"B": 1, "A": 1}

    # A2 依赖 B2，但根要求 B1，无解
    assert resolve(repo, {"A": {2}, "B": {1}}) is None

    # 依赖环本身不是错误
    cyclic = {"A": {1: {"B": {1}}}, "B": {1: {"A": {1}}}}
    assert resolve(cyclic, {"A": {1}}) == {"A": 1, "B": 1}

    # 仓库里没有的包无法满足
    assert resolve(repo, {"X": {1}}) is None

    # 需要回溯：先试的 A1 会把 C 限制到不存在的版本
    backtrack = {
        "A": {1: {"C": {9}}, 2: {"C": {1}}},
        "C": {1: {}},
    }
    assert resolve(backtrack, {"A": {1, 2}}) == {"A": 2, "C": 1}


if __name__ == "__main__":
    test()
