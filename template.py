import AlteryxPythonSDK as Sdk
import xml.etree.ElementTree as Et


class AyxPlugin:
    def __init__(self, n_tool_id: int, alteryx_engine: object, output_anchor_mgr: object):
        # Default properties
        self.n_tool_id: int = n_tool_id
        self.alteryx_engine: Sdk.AlteryxEngine = alteryx_engine
        self.output_anchor_mgr: Sdk.OutputAnchorManager = output_anchor_mgr
        self.label = "Template (" + str(n_tool_id) + ")"

        # Custom properties
        self.TextValue: str = None
        self.NumericField: str = None
        self.DateField: str = None

    def pi_init(self, str_xml: str):
        xml_parser = Et.fromstring(str_xml)
        self.TextValue = xml_parser.find("TextValue").text if 'TextValue' in str_xml else ''
        self.NumericField = xml_parser.find("NumericField").text if 'NumericField' in str_xml else ''
        self.DateField = xml_parser.find("DateField").text if 'DateField' in str_xml else ''

        # Getting the output anchor from Config.xml by the output connection name
        self.Output = self.output_anchor_mgr.get_output_anchor('Output')

    def pi_add_incoming_connection(self, str_type: str, str_name: str) -> object:
        return IncomingInterface(self)

    def pi_add_outgoing_connection(self, str_name: str) -> bool:
        return True

    def pi_push_all_records(self, n_record_limit: int) -> bool:
        return False

    def pi_close(self, b_has_errors: bool):
        return

    def display_error_msg(self, msg_string: str):
        self.alteryx_engine.output_message(self.n_tool_id, Sdk.EngineMessageType.error, msg_string)

    def display_info_msg(self, msg_string: str):
        self.alteryx_engine.output_message(self.n_tool_id, Sdk.EngineMessageType.info, msg_string)


class IncomingInterface:
    def __init__(self, parent: AyxPlugin):
        # Default properties
        self.parent: AyxPlugin = parent

        # Custom properties
        self.InInfo: Sdk.RecordInfo = None
        self.OutInfo: Sdk.RecordInfo = None
        self.Creator: Sdk.RecordCreator = None
        self.Copier: Sdk.RecordCopier = None

    def ii_init(self, record_info_in: Sdk.RecordInfo) -> bool:
        self.InInfo = record_info_in
        self.OutInfo = self.InInfo.clone()
        self.Creator = self.OutInfo.construct_record_creator()
        self.Copier = Sdk.RecordCopier(self.OutInfo, self.InInfo)

        index = 0
        while index < self.InInfo.num_fields:
            self.Copier.add(index, index)
            index += 1
        self.Copier.done_adding()
        self.parent.Output.init(self.OutInfo)
        return True

    def ii_push_record(self, in_record: Sdk.RecordRef) -> bool:
        self.Creator.reset()
        self.Copier.copy(self.Creator, in_record)
        out_record = self.Creator.finalize_record()
        self.parent.Output.push_record(out_record)
        return True

    def ii_update_progress(self, d_percent: float):
        # Inform the Alteryx engine of the tool's progress.
        self.parent.alteryx_engine.output_tool_progress(self.parent.n_tool_id, d_percent)

    def ii_close(self):
        self.parent.Output.assert_close()
        return
