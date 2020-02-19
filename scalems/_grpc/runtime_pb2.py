# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: scalems/_grpc/runtime.proto

from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='scalems/_grpc/runtime.proto',
  package='scalems.runtime',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=b'\n\x1bscalems/_grpc/runtime.proto\x12\x0fscalems.runtime\"\x14\n\x04Node\x12\x0c\n\x04uuid\x18\x01 \x01(\x0c\"H\n\x08\x45nsemble\x12\x0c\n\x04size\x18\x01 \x01(\x05\x12\x11\n\tmember_id\x18\x02 \x01(\x05\x12\x1b\n\x13\x65nsemble_identifier\x18\x03 \x01(\x0c\"\xa1\x01\n\x07\x43ommand\x12\x35\n\x0binstruction\x18\x01 \x01(\x0e\x32 .scalems.runtime.InstructionEnum\x12%\n\x04node\x18\x02 \x01(\x0b\x32\x15.scalems.runtime.NodeH\x00\x12-\n\x08\x65nsemble\x18\x10 \x01(\x0b\x32\x19.scalems.runtime.EnsembleH\x00\x42\t\n\x07payload\"\xa6\x01\n\nWorkerNote\x12.\n\x04note\x18\x01 \x01(\x0e\x32 .scalems.runtime.WorkerNote.Note\x12%\n\x04node\x18\x02 \x01(\x0b\x32\x15.scalems.runtime.NodeH\x00\x12\x0e\n\x04name\x18\x03 \x01(\tH\x00\"&\n\x04Note\x12\x0b\n\x07PUBLISH\x10\x00\x12\x11\n\rRESOURCE_NAME\x10\x01\x42\t\n\x07payload*R\n\x0fInstructionEnum\x12\t\n\x05PLACE\x10\x00\x12\r\n\tSUBSCRIBE\x10\x01\x12\x12\n\x0e\x45NTER_ENSEMBLE\x10\x03\x12\x11\n\rEXIT_ENSEMBLE\x10\x04\x32O\n\x06Worker\x12\x45\n\x06Update\x12\x18.scalems.runtime.Command\x1a\x1b.scalems.runtime.WorkerNote\"\x00(\x01\x30\x01\x62\x06proto3'
)

_INSTRUCTIONENUM = _descriptor.EnumDescriptor(
  name='InstructionEnum',
  full_name='scalems.runtime.InstructionEnum',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='PLACE', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SUBSCRIBE', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ENTER_ENSEMBLE', index=2, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='EXIT_ENSEMBLE', index=3, number=4,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=477,
  serialized_end=559,
)
_sym_db.RegisterEnumDescriptor(_INSTRUCTIONENUM)

InstructionEnum = enum_type_wrapper.EnumTypeWrapper(_INSTRUCTIONENUM)
PLACE = 0
SUBSCRIBE = 1
ENTER_ENSEMBLE = 3
EXIT_ENSEMBLE = 4


_WORKERNOTE_NOTE = _descriptor.EnumDescriptor(
  name='Note',
  full_name='scalems.runtime.WorkerNote.Note',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='PUBLISH', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='RESOURCE_NAME', index=1, number=1,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=426,
  serialized_end=464,
)
_sym_db.RegisterEnumDescriptor(_WORKERNOTE_NOTE)


_NODE = _descriptor.Descriptor(
  name='Node',
  full_name='scalems.runtime.Node',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='uuid', full_name='scalems.runtime.Node.uuid', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=48,
  serialized_end=68,
)


_ENSEMBLE = _descriptor.Descriptor(
  name='Ensemble',
  full_name='scalems.runtime.Ensemble',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='size', full_name='scalems.runtime.Ensemble.size', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='member_id', full_name='scalems.runtime.Ensemble.member_id', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ensemble_identifier', full_name='scalems.runtime.Ensemble.ensemble_identifier', index=2,
      number=3, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=70,
  serialized_end=142,
)


_COMMAND = _descriptor.Descriptor(
  name='Command',
  full_name='scalems.runtime.Command',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instruction', full_name='scalems.runtime.Command.instruction', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='node', full_name='scalems.runtime.Command.node', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ensemble', full_name='scalems.runtime.Command.ensemble', index=2,
      number=16, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='payload', full_name='scalems.runtime.Command.payload',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=145,
  serialized_end=306,
)


_WORKERNOTE = _descriptor.Descriptor(
  name='WorkerNote',
  full_name='scalems.runtime.WorkerNote',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='note', full_name='scalems.runtime.WorkerNote.note', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='node', full_name='scalems.runtime.WorkerNote.node', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='name', full_name='scalems.runtime.WorkerNote.name', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _WORKERNOTE_NOTE,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='payload', full_name='scalems.runtime.WorkerNote.payload',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=309,
  serialized_end=475,
)

_COMMAND.fields_by_name['instruction'].enum_type = _INSTRUCTIONENUM
_COMMAND.fields_by_name['node'].message_type = _NODE
_COMMAND.fields_by_name['ensemble'].message_type = _ENSEMBLE
_COMMAND.oneofs_by_name['payload'].fields.append(
  _COMMAND.fields_by_name['node'])
_COMMAND.fields_by_name['node'].containing_oneof = _COMMAND.oneofs_by_name['payload']
_COMMAND.oneofs_by_name['payload'].fields.append(
  _COMMAND.fields_by_name['ensemble'])
_COMMAND.fields_by_name['ensemble'].containing_oneof = _COMMAND.oneofs_by_name['payload']
_WORKERNOTE.fields_by_name['note'].enum_type = _WORKERNOTE_NOTE
_WORKERNOTE.fields_by_name['node'].message_type = _NODE
_WORKERNOTE_NOTE.containing_type = _WORKERNOTE
_WORKERNOTE.oneofs_by_name['payload'].fields.append(
  _WORKERNOTE.fields_by_name['node'])
_WORKERNOTE.fields_by_name['node'].containing_oneof = _WORKERNOTE.oneofs_by_name['payload']
_WORKERNOTE.oneofs_by_name['payload'].fields.append(
  _WORKERNOTE.fields_by_name['name'])
_WORKERNOTE.fields_by_name['name'].containing_oneof = _WORKERNOTE.oneofs_by_name['payload']
DESCRIPTOR.message_types_by_name['Node'] = _NODE
DESCRIPTOR.message_types_by_name['Ensemble'] = _ENSEMBLE
DESCRIPTOR.message_types_by_name['Command'] = _COMMAND
DESCRIPTOR.message_types_by_name['WorkerNote'] = _WORKERNOTE
DESCRIPTOR.enum_types_by_name['InstructionEnum'] = _INSTRUCTIONENUM
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Node = _reflection.GeneratedProtocolMessageType('Node', (_message.Message,), {
  'DESCRIPTOR' : _NODE,
  '__module__' : 'scalems._grpc.runtime_pb2'
  # @@protoc_insertion_point(class_scope:scalems.runtime.Node)
  })
_sym_db.RegisterMessage(Node)

Ensemble = _reflection.GeneratedProtocolMessageType('Ensemble', (_message.Message,), {
  'DESCRIPTOR' : _ENSEMBLE,
  '__module__' : 'scalems._grpc.runtime_pb2'
  # @@protoc_insertion_point(class_scope:scalems.runtime.Ensemble)
  })
_sym_db.RegisterMessage(Ensemble)

Command = _reflection.GeneratedProtocolMessageType('Command', (_message.Message,), {
  'DESCRIPTOR' : _COMMAND,
  '__module__' : 'scalems._grpc.runtime_pb2'
  # @@protoc_insertion_point(class_scope:scalems.runtime.Command)
  })
_sym_db.RegisterMessage(Command)

WorkerNote = _reflection.GeneratedProtocolMessageType('WorkerNote', (_message.Message,), {
  'DESCRIPTOR' : _WORKERNOTE,
  '__module__' : 'scalems._grpc.runtime_pb2'
  # @@protoc_insertion_point(class_scope:scalems.runtime.WorkerNote)
  })
_sym_db.RegisterMessage(WorkerNote)



_WORKER = _descriptor.ServiceDescriptor(
  name='Worker',
  full_name='scalems.runtime.Worker',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=561,
  serialized_end=640,
  methods=[
  _descriptor.MethodDescriptor(
    name='Update',
    full_name='scalems.runtime.Worker.Update',
    index=0,
    containing_service=None,
    input_type=_COMMAND,
    output_type=_WORKERNOTE,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_WORKER)

DESCRIPTOR.services_by_name['Worker'] = _WORKER

# @@protoc_insertion_point(module_scope)
