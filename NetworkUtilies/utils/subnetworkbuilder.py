from NetworkUtilies.core.network_basic import NetworkBasic


class SubnetworkBuilder(NetworkBasic):
    subnets_sizes, subnets, submasks_machine_bits = [], [], []

    def __display_subnets(self, advanced):

        # graph
        occupied = 0
        for i in range(len(self.submasks_machine_bits)):
            occupied += 2 ** self.submasks_machine_bits[i] - 2
        percentage = round((occupied / self.addresses) * 100)
        graph = '['
        current = 0
        for i in range(20):
            if current < percentage:
                graph += '█'
            else:
                graph += '░'
            current += 5
        graph += "] {} %".format(percentage)

        if self.lang == 'en':
            if len(self.subnets) > 1:
                t = 's'
            else:
                t = ''
        else:
            if len(self.subnets) > 1:
                t = 'x'
            else:
                t = ''

        print(self.lang_dict[self.lang]['network'])
        if advanced is True:
            print(self.lang_dict[self.lang]['cidr_adv'].format(self.ip, self.mask_length))
        else:
            print(self.lang_dict[self.lang]['cidr'].format(self.ip, self.mask_length))
        print("{} - {}".format(self.network_range['start'], self.network_range['end']))
        if advanced is True:
            print(self.lang_dict[self.lang]['addr_avail_advanced'].format(occupied, self.addresses))
        else:
            print(self.lang_dict[self.lang]['addr_avail'].format(self.addresses))
        print('')
        print(self.lang_dict[self.lang]['utils'].format(len(self.subnets), t))

        for i in range(len(self.subnets)):
            if advanced is True:
                print(self.lang_dict[self.lang]['sub_addr_advanced'].format(self.subnets[i]['start'],
                                                                            self.subnets[i]['end'],
                                                                            2 ** self.submasks_machine_bits[i] - 2,
                                                                            self.subnets_sizes[i]))
            else:
                print(self.lang_dict[self.lang]['sub_addr'].format(self.subnets[i]['start'], self.subnets[i]['end'],
                                                                   2 ** self.submasks_machine_bits[i] - 2))

        print('')
        print(self.lang_dict[self.lang]['net_usage'])
        print(graph)

    def _find_start_of_next_subnet_range(self, end):
        def _check(idx, content):
            if idx == 0 and content[idx] == '255':
                raise Exception(self.error_dict[self.lang]['network_limit'])

            if content[idx] == '255':
                content[idx] = '0'
                return _check(idx - 1, content)
            else:
                content[idx] = str(int(content[idx]) + 1)
                return '.'.join(content)

        data = end.split('.')
        return _check(3, data)

    def __determine_required_submasks_sizes(self):

        submasks = []

        for i in range(len(self.subnets_sizes)):
            power = 1
            while 2 ** power - 2 < self.subnets_sizes[i]:
                power = power + 1
            submasks.append(power)

        self.submasks_machine_bits = submasks

    def __init__(self, starting_ip, mask, subnets_sizes, lang=None):
        super().__init__(starting_ip, mask, lang=lang)
        self.subnets_sizes = sorted(subnets_sizes, reverse=True)

        # first, let's check if the provided mask can handle all the addresses requested
        self.determine_network_range()
        self.__determine_required_submasks_sizes()

        total = 0

        for i in range(len(self.submasks_machine_bits)):
            total += 2**self.submasks_machine_bits[i]

        if self.addresses < total:
            power = 1
            while total > 2**power:
                power += 1
            raise Exception(self.error_dict[self.lang]['mask_too_small'].format(self.mask_length, 32-power))

    def build_subnets(self, returning=None, display=None, advanced=None):

        start_ip = self.network_range['start']

        for i in range(len(self.subnets_sizes)):
            machine_bits = self.submasks_machine_bits[i]
            result = self.determine_network_range(returning=True, start_ip=start_ip, machine_bits=machine_bits)
            self.subnets.append(result)
            start_ip = self._find_start_of_next_subnet_range(result['end'])

        if display is True:
            self.__display_subnets(advanced)
        elif display is False:
            print(self.subnets)

        if returning is True:
            return self.subnets
