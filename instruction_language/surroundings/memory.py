import os
import uuid

class MemoryManager:
    def __init__(self):
        self.namespace_register: dict[dict] = {}
        self.namespace_stack: list[str] = []


    def get_var(self, namespace_uuid, key):
        self._collect_garbage(namespace_uuid)

        for namespace_uuid in reversed(self.namespace_stack):
            namespace = self.namespace_register[namespace_uuid]
            if key in namespace:
                return namespace[key]
        return None
    
    def set_var(self, namespace_uuid, key, value):
        self._collect_garbage(namespace_uuid)

        self.namespace_register[namespace_uuid][key] = value

    def new_namespace(self):
        namespace_uuid = str(uuid.uuid4())
        self.namespace_register[namespace_uuid] = {}
        self.namespace_stack.append(namespace_uuid)

        return namespace_uuid

    def _collect_garbage(self, requested_uuid):
        if len(self.namespace_stack) > 1 and self.namespace_stack[-1] != requested_uuid and requested_uuid in self.namespace_stack[0:-1]:
            self.namespace_stack.pop()


class GMMService:
    """
    (Global Memory Manager Service)
    The purpose of this class is to manage instances of the MemoryManager so the it is not necessary to pass the instances through each codeblock of an execution plan.
    The only thing the caller needs to care about is to use unique identifier to prevent unexpected state behavior in the program.
    """
    
    _memory_manager_register: dict[str, MemoryManager] = {}

    @staticmethod
    # def get(id=os.environ.get("MEMORY_MANAGER_ID")):
    def get(id=None):
        if id is None:
            id = os.environ.get("MEMORY_MANAGER_ID")

        if id not in GMMService._memory_manager_register.keys():
            GMMService._memory_manager_register[id] = MemoryManager()

        return GMMService._memory_manager_register[id]
    
    @staticmethod
    def delete(id=os.environ.get("MEMORY_MANAGER_ID")):
        if id in GMMService._memory_manager_register.keys():
            del GMMService._memory_manager_register[id]
