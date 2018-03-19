class node:

    def __init__(self, value, neighbors):
        self.value = value
        self.neighbors = neighbors


if __name__ == '__main__':
    head = node(0, [
        node(1, [
            node(2, [
                node(3, []),
                node(4, []),
                node(5, [])
            ]),
            node(6, []),
            node(7, [
                node(8, []),
                node(9, [
                    node(10, [])
                ])
            ])
        ]),
        node(11, [])
    ])

    s = [head]
    while len(s) > 0:
        curr = s.pop()
        s.extend(reversed(curr.neighbors))
        print('current value:', curr.value)
