"""
Expected requests

    "initialize": self.serve_initialize,
    "initialized": self.serve_ignore,
    "textDocument/didOpen": self.serve_doc_did_open,
    "textDocument/didChange": self.serve_doc_did_change,
    "textDocument/completion": self.serve_completion,
    "textDocument/hover": self.serve_hover,
    "textDocument/codeAction": self.serve_available_commands,
    "textDocument/implementation":
    "textDocument/definition": self.serve_definition,
    "textDocument/xdefinition": self.serve_x_definition,
    "textDocument/references": self.serve_references,
    "workspace/xreferences": self.serve_x_references,
    "textDocument/documentSymbol": self.serve_document_symbols,
    "workspace/symbol": self.serve_symbols,
    "workspace/xpackages": self.serve_x_packages,
    "workspace/xdependencies": self.serve_x_dependencies,
    "$/cancelRequest": self.serve_ignore,
    "shutdown": self.serve_ignore,
    "exit": self.serve_exit,

"""
#  Copyright (c) 2019 Seven Bridges. See LICENSE

from enum import IntEnum

from .lspobjects import to_dict
from .base import CWLLangServerBase, JSONRPC2Error, ServerError, LSPErrCode
from .fileoperation import FileOperation
from .definition import Definition
from .completion import Completion
from .documentsymbol import DocumentSymbol
from .hover import Hover
from .formatting import Formatting

import logging

logger = logging.getLogger(__name__)
logger.propagate = True

logging.getLogger("benten.langserver.jsonrpc").propagate = False


class TextDocumentSyncKind(IntEnum):
    _None = 0
    Full = 1
    Incremental = 2


class LangServer(
        Formatting,
        Hover,
        DocumentSymbol,
        Completion,
        Definition,
        FileOperation,
        CWLLangServerBase):

    def run(self):
        while self.running:
            try:
                request = self.conn.read_message()
                self.handle(request)
            except EOFError:
                break
            except Exception as e:
                logger.error("Unexpected error: %s", e, exc_info=True)

    # Request message:
    # {
    # 	"jsonrpc": "2.0",
    # 	"id": 1, # <----------  if this field is missing, it's a notification
    #                       	and should not receive a response. Otherwise,
    #                           the response should carry this id for accounting
    #                           purposes
    # 	"method": "...",
    # 	"params": {
    # 		...
    # 	}
    # }
    def handle(self, client_query):
        logger.info("Client query: {}".format(client_query.get("method")))

        is_a_request = "id" in client_query

        if self.premature_request(client_query, is_a_request):
            return

        if self.duplicate_initialization(client_query, is_a_request):
            return

        try:
            response = to_dict(self._dispatch(client_query))

            if is_a_request:
                self.conn.write_response(client_query["id"], response)

        except ServerError as e:
            logger.error(e.server_error_message)

            let_client_know_of_errors = False
            if let_client_know_of_errors:
                self.conn.write_error(
                    client_query["id"],
                    code=e.json_rpc_error.code,
                    message=str(e.json_rpc_error.message),
                    data=e.json_rpc_error.data)

    def premature_request(self, client_query, is_a_request):
        if not self.initialization_request_received and \
                client_query.get("method", None) not in ["initialize", "exit"]:
            logger.warning("Client sent a request/notification without initializing")
            if is_a_request:
                self.conn.write_error(
                    client_query["id"],
                    code=LSPErrCode.ServerNotInitialized,
                    message="",
                    data={})
            return True
        else:
            return False

    def duplicate_initialization(self, client_query, is_a_request):
        if self.initialization_request_received and client_query.get("method", None) == "initialize":
            logger.warning("Client sent duplicate initialization")
            if is_a_request:
                self.conn.write_error(
                    client_query["id"],
                    code=LSPErrCode.InvalidRequest,
                    message="Client sent duplicate initialization",
                    data={})
            return True
        else:
            return False

    def _dispatch(self, client_query):
        # textDocument/didOpen -> serve_textDocument_didOpen
        method_name = "serve_" + client_query.get("method", "noMethod").replace("/", "_")
        try:
            f = getattr(self, method_name)
        except AttributeError as e:
            f = self.serve_unknown
        return f(client_query)

    @staticmethod
    def serve_noMethod(client_query):
        msg = "Method not specified"
        raise ServerError(
            server_error_message=msg,
            json_rpc_error=JSONRPC2Error(
                code=LSPErrCode.MethodNotFound,
                message=msg))

    @staticmethod
    def serve_unknown(client_query):
        msg = "Unknown method: {}".format(client_query["method"])
        raise ServerError(
            server_error_message=msg,
            json_rpc_error=JSONRPC2Error(
                code=LSPErrCode.MethodNotFound,
                message=msg))

    def serve_shutdown(self, client_query):
        logging.shutdown()
        self.running = False

    # https://microsoft.github.io/language-server-protocol/specification#initialize
    def serve_initialize(self, client_query):
        self.initialization_request_received = True

        self.client_capabilities = client_query.get("capabilities", {})
        logger.debug("InitOpts: {}".format(client_query))

        return {
            "capabilities": {
                "textDocumentSync": TextDocumentSyncKind.Full,
                #  Avoid complexity of incremental updates for now
                "completionProvider": {
                    "resolveProvider": True,
                    "triggerCharacters": [".", "/"]
                },
                "hoverProvider": True,
                "definitionProvider": True,
                "referencesProvider": True,
                "documentSymbolProvider": True,
                "workspaceSymbolProvider": True,
                "streaming": True,
                "codeActionProvider": {
                    "codeActionKinds": ["source"]
                },
                "documentFormattingProvider": True,
                "workspace": {
                    "workspaceFolders": {
                        "supported": True,
                        "changeNotifications": True
                    }
                },
                # https://github.com/sourcegraph/language-server-protocol/blob/master/extension-files.md#files-extensions-to-lsp
                # This is not in the spec yet
                "xfilesProvider": True
            }
        }

    @staticmethod
    def serve_initialized(client_query):
        return {}

