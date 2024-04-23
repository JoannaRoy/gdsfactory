from __future__ import annotations

from functools import partial

import gdsfactory as gf
from gdsfactory.component import Component
from gdsfactory.components.wire import wire_straight
from gdsfactory.port import select_ports_electrical
from gdsfactory.routing.route_quad import route_quad
from gdsfactory.typings import Callable, ComponentSpec, Strs

_wire_long = partial(wire_straight, length=200.0)


@gf.cell_with_child
def add_electrical_pads_shortest(
    component: ComponentSpec = _wire_long,
    pad: ComponentSpec = "pad",
    pad_port_spacing: float = 50.0,
    select_ports: Callable = select_ports_electrical,
    port_names: Strs | None = None,
    port_orientation: float = 90,
    layer: gf.typings.LayerSpec = "M3",
) -> Component:
    """Returns new Component with a pad by each electrical port.

    Args:
        component: to route.
        pad: pad element or function.
        pad_port_spacing: spacing between pad and port.
        select_ports: function to select ports.
        port_orientation: in degrees.
        port_names: optional port names. Overrides select_ports.
        layer: for the routing.

    .. plot::
        :include-source:

        import gdsfactory as gf
        c = gf.components.straight_heater_metal(length=100)
        wire_long = gf.components.wire_straight(length=200.)
        c = gf.routing.add_electrical_pads_shortest(wire_long)
        c.plot()

    """
    c = Component()
    component = gf.get_component(component)
    pad = gf.get_component(pad)
    ref = c << component
    ports = (
        [ref[port_name] for port_name in port_names]
        if port_names
        else select_ports(ref.ports)
    )
    ports = list(ports.values())

    pad_port_spacing += pad.info["xsize"] / 2

    for i, port in enumerate(ports):
        p = c << pad

        if port_orientation == 0:
            p.x = port.x + pad_port_spacing
            p.y = port.y
            c.add_ref(route_quad(port, p.ports["e1"], layer=layer))
        elif port_orientation == 180:
            p.x = port.x - pad_port_spacing
            p.y = port.y
            c.add_ref(route_quad(port, p.ports["e3"], layer=layer))
        elif port_orientation == 90:
            p.y = port.y + pad_port_spacing
            p.x = port.x
            c.add_ref(route_quad(port, p.ports["e4"], layer=layer))
        elif port_orientation == 270:
            p.y = port.y - pad_port_spacing
            p.x = port.x
            c.add_ref(route_quad(port, p.ports["e2"], layer=layer))

        c.add_port(port=p.ports["pad"], name=f"elec-{component.name}-{i+1}")

    c.add_ports(ref.ports)

    for port in ports:
        c.ports.pop(port.name)
    c.copy_child_info(component)
    return c


if __name__ == "__main__":
    # c = gf.components.cross(length=100, layer=(49, 0))
    # c = gf.components.mzi_phase_shifter()
    # c = gf.components.straight_heater_metal(length=100)
    # c = add_electrical_pads_shortest(component=c, port_orientation=270)
    c = add_electrical_pads_shortest()
    c.show(show_ports=True)
