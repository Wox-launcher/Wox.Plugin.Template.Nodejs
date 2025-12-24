import { ActionContext, Context, Plugin, PluginInitParams, PublicAPI, Query, Result } from "@wox-launcher/wox-plugin"

let api: PublicAPI

export const plugin: Plugin = {
  init: async (ctx: Context, initParams: PluginInitParams) => {
    api = initParams.API
    await api.Log(ctx, "Info", "Init finished")
  },

  query: async (ctx: Context, query: Query): Promise<Result[]> => {
    return [
      {
        Title: "Hello World " + query.Search,
        SubTitle: "This is a subtitle",
        Icon: {
          ImageType: "relative",
          ImageData: "images/app.png"
        },
        Preview: {
          PreviewType: "text",
          PreviewData: "This is a preview",
          PreviewProperties: {
            Property1: "Hello World",
            Property2: "This is a property"
          }
        },
        Tails: [
          {
            Type: "text",
            Text: "This is a tail"
          }
        ],
        Actions: [
          {
            Name: "Open",
            ContextData: {
              search: query.Search
            },
            Action: async (actionCtx: Context, actionContext: ActionContext) => {
              await api.Log(actionCtx, "Info", `Open action executed with search: ${actionContext.ContextData.search}`)
              await api.Notify(actionCtx, `You searched for: ${actionContext.ContextData.search}`)
            }
          }
        ]
      }
    ]
  }
}
