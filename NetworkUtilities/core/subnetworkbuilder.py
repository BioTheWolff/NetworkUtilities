from NetworkUtilities.core.network_basic import NetworkBasic
from NetworkUtilities.utils.errors import MaskTooSmallException
from NetworkUtilities.utils.utils import Utils
from typing import Union, List, Optional


class SubnetworkBuilder(NetworkBasic):
    total_network_range = {}
    subnets_sizes, subnets, submasks_machine_bits = [], [], []

    def __build_graph(self):
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

        if len(self.subnets) > 1:
            t = 's'
        else:
            t = ''

        return occupied, graph, t

    def __display_subnets(self, advanced=False) -> None:

        occupied, graph, t = self.__build_graph()

        literal_ip = Utils.to_literal(self.ip)
        literal_netr = Utils.netr_to_literal(self.total_network_range)

        print(self.lang_dict['network'])
        if advanced is True:
            print(self.lang_dict['cidr_adv'].format(literal_ip, self.mask_length))
        else:
            print(self.lang_dict['cidr'].format(literal_ip, self.mask_length))
        print("{} - {}".format(literal_netr['start'], literal_netr['end']))
        if advanced is True:
            print(self.lang_dict['addr_avail_advanced'].format(occupied, self.addresses))
        else:
            print(self.lang_dict['addr_avail'].format(self.addresses))
        print('')
        print(self.lang_dict['utils'].format(len(self.subnets), t))

        for i in range(len(self.subnets)):
            literal_sub_netr = Utils.netr_to_literal(self.subnets[i])

            if advanced:
                print(self.lang_dict['sub_addr_advanced'].format(literal_sub_netr['start'],
                                                                 literal_sub_netr['end'],
                                                                 2 ** self.submasks_machine_bits[i] - 2,
                                                                 self.subnets_sizes[i]))
            else:
                print(self.lang_dict['sub_addr'].format(literal_sub_netr['start'],
                                                        literal_sub_netr['end'],
                                                        2 ** self.submasks_machine_bits[i] - 2))

        if advanced:
            print('')
            print(self.lang_dict['net_usage'])
            print(graph)

    def __to_printable_subnets(self):
        return [Utils.netr_to_literal(i) for i in self.subnets]

    def __determine_required_submasks_sizes(self) -> None:

        submasks = []

        for i in range(len(self.subnets_sizes)):
            power = 1
            while 2 ** power - 2 < self.subnets_sizes[i]:
                power += 1
            submasks.append(power)

        self.submasks_machine_bits = submasks

    def __init__(self, starting_ip: str, mask: Union[str, int], subnets_sizes: List[int]) -> None:
        super().__init__(starting_ip, mask)
        self.subnets_sizes = sorted(subnets_sizes, reverse=True)

        # first, let's check if the provided mask can handle all the addresses requested
        self.total_network_range = self.determine_network_range()
        self.__determine_required_submasks_sizes()

        total = 0

        for i in range(len(self.submasks_machine_bits)):
            total += 2 ** self.submasks_machine_bits[i]

        if self.addresses < total:
            power = 1
            while total > 2 ** power:
                power += 1
            raise MaskTooSmallException(self.mask_length, 32 - power)

    def build_subnets(self, display: Optional[bool] = None, advanced: Optional[bool] = None):
        start_ip = self.network_range['start']

        for i in range(len(self.subnets_sizes)):
            machine_bits = self.submasks_machine_bits[i]
            result = self.determine_network_range(ip=start_ip, machine_bits=machine_bits)
            self.subnets.append(result)
            start_ip = Utils.ip_after(result['end'])

        if display is True:
            self.__display_subnets(advanced)
        elif display is False:
            print(self.__to_printable_subnets())

        return self.subnets