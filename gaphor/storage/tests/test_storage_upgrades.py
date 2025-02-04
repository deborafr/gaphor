import pytest

from gaphor.storage.parser import element
from gaphor.storage.storage import load_elements
from gaphor.storage.upgrade_canvasitem import upgrade_canvasitem
from gaphor.UML import diagramitems


@pytest.fixture
def loader(element_factory, modeling_language):
    def _loader(*parsed_items):
        for item in parsed_items:
            item.references["diagram"] = "1"
            upgrade_canvasitem(item, "1.0.0")
        parsed_data = {
            "1": element(id="1", type="Diagram"),
            **{p.id: p for p in parsed_items},
        }
        load_elements(parsed_data, element_factory, modeling_language)
        return list(element_factory.lselect()[0].get_all_items())

    return _loader


def test_upgrade_metaclass_item_to_class_item(loader):
    item = loader(element(id="2", type="MetaclassItem"))[0]

    assert type(item) == diagramitems.ClassItem


def test_upgrade_subsystem_item_to_class_item(loader):
    item = loader(element(id="2", type="SubsystemItem"))[0]

    assert type(item) == diagramitems.ComponentItem


def test_rename_stereotype_attrs_field(loader):
    parsed_item = element(id="2", type="ClassItem")
    parsed_item.values["show_stereotypes_attrs"] = "1"
    item = loader(parsed_item)[0]

    assert not hasattr(item, "show_stereotypes_attrs")
    assert item.show_stereotypes


def test_rename_show_attributes_and_operations_field(loader):
    parsed_item = element(id="2", type="ClassItem")
    parsed_item.values["show-attributes"] = "0"
    parsed_item.values["show-operations"] = "0"
    item = loader(parsed_item)[0]

    assert not item.show_attributes
    assert not item.show_operations


def test_interface_drawing_style_normal(loader):
    parsed_item = element(id="2", type="InterfaceItem")
    parsed_item.values["drawing-style"] = "0"  # DRAW_NONE
    item = loader(parsed_item)[0]

    assert item.folded.name == "NONE"


def test_interface_drawing_style_folded(loader):
    parsed_item = element(id="2", type="InterfaceItem")
    parsed_item.values["drawing-style"] = "3"  # DRAW_ICON
    item = loader(parsed_item)[0]

    assert item.folded.name == "PROVIDED"


def test_upgrade_generalization_arrow_direction(loader):
    cls1 = element(id="2", type="ClassItem")
    cls2 = element(id="3", type="ClassItem")
    gen_item = element(id="4", type="GeneralizationItem")
    gen_item.references["head-connection"] = ["2"]
    gen_item.references["tail-connection"] = ["3"]

    cls1, cls2, gen_item = loader(cls1, cls2, gen_item)

    assert gen_item.diagram.connections.get_connection(gen_item.head).connected is cls2
    assert gen_item.diagram.connections.get_connection(gen_item.tail).connected is cls1
