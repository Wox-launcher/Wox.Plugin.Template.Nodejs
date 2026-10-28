import { Context, PublicAPI, Query, WoxImage } from "@wox-launcher/wox-plugin"
import { plugin } from "../index"

test("query", async () => {
  const ctx = {} as Context
  const notify = jest.fn().mockResolvedValue(undefined)
  const log = jest.fn().mockResolvedValue(undefined)
  const query = {
    Id: "1",
    Env: { ActiveWindowTitle: "", ActiveWindowPid: 0, ActiveBrowserUrl: "", ActiveWindowIcon: {} as WoxImage },
    RawQuery: "wpm install ",
    Selection: { Type: "text", Text: "", FilePaths: [] },
    Type: "input",
    Search: "",
    TriggerKeyword: "wpm",
    Command: "install",
    IsGlobalQuery(): boolean {
      return false
    }
  } as Query

  await plugin.init(ctx, {
    PluginDirectory: "",
    API: {
      Log: log,
      Notify: notify
    } as unknown as PublicAPI
  })
  const response = await plugin.query(ctx, query)
  expect(Array.isArray(response)).toBe(false)
  if (Array.isArray(response)) throw new Error("Expected QueryResponse")
  expect(response.Results[0].Title).toBe("Hello World ")
  const action = response.Results[0].Actions?.[0]
  if (!action || action.Type === "form") throw new Error("Expected an execute action")
  await action.Action(ctx, { ResultId: "1", ResultActionId: "1", ContextData: action.ContextData ?? {} })
  expect(notify).toHaveBeenCalledWith(ctx, "You searched for: ")
})
