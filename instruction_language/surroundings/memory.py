import os
import uuid


class MemoryManager:
    current_namespace_id: str = None
    namespace_register: dict[dict] = {}
    namespace_stack: list[str] = []

    @staticmethod
    def get_var(key, namespace_uuid=None):
        if namespace_uuid is None:
            namespace_uuid = MemoryManager.current_namespace_id

        MemoryManager._collect_garbage(namespace_uuid)

        for namespace_uuid in reversed(MemoryManager.namespace_stack):
            namespace = MemoryManager.namespace_register[namespace_uuid]
            if key in namespace:
                return namespace[key]
        return None

    @staticmethod
    def set_var(key, value, namespace_uuid=None):
        if namespace_uuid is None:
            namespace_uuid = MemoryManager.current_namespace_id

        MemoryManager._collect_garbage(namespace_uuid)

        MemoryManager.namespace_register[namespace_uuid][key] = value

    @staticmethod
    def new_namespace():
        namespace_uuid = str(uuid.uuid4())
        MemoryManager.namespace_register[namespace_uuid] = {}
        MemoryManager.namespace_stack.append(namespace_uuid)

        MemoryManager.current_namespace_id = namespace_uuid

        return namespace_uuid

    @staticmethod
    def _collect_garbage(requested_uuid):
        if len(MemoryManager.namespace_stack) > 1 and MemoryManager.namespace_stack[-1] != requested_uuid and requested_uuid in MemoryManager.namespace_stack[0:-1]:
            MemoryManager.namespace_stack.pop()

    @staticmethod
    def reset():
        """
        Reset the whole memory manager to its initial state.
        """
        MemoryManager.current_namespace_id = None
        MemoryManager.namespace_register = {}
        MemoryManager.namespace_stack = []


# class GMMService:
#     """
#     (Global Memory Manager Service)
#     The purpose of this class is to manage instances of the MemoryManager so the it is not necessary to pass the instances through each codeblock of an execution plan.
#     The only thing the caller needs to care about is to use unique identifier to prevent unexpected state behavior in the program.
#     """

#     _memory_manager_register: dict[str, MemoryManager] = {}

#     @staticmethod
#     # def get(id=os.environ.get("MEMORY_MANAGER_ID")):
#     def get(id=None):
#         if id is None:
#             id = os.environ.get("MEMORY_MANAGER_ID")

#         if id not in GMMService._memory_manager_register.keys():
#             GMMService._memory_manager_register[id] = MemoryManager()

#         return GMMService._memory_manager_register[id]

#     @staticmethod
#     def delete(id=os.environ.get("MEMORY_MANAGER_ID")):
#         if id in GMMService._memory_manager_register.keys():
#             del GMMService._memory_manager_register[id]
