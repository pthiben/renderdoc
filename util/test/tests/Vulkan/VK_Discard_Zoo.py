import rdtest
import struct
import renderdoc as rd


class VK_Discard_Zoo(rdtest.Discard_Zoo):
    demos_test_name = 'VK_Discard_Zoo'
    internal = False

    def __init__(self):
        rdtest.Discard_Zoo.__init__(self)

    def check_capture(self):
        self.check_textures()

        # Test render pass attachments
        draw = self.find_draw("TestStart")

        rpcol: rd.TextureDescription = self.get_texture(
            [res for res in self.controller.GetResources() if "RPCol" in res.name][0].resourceId)
        rpdepth: rd.TextureDescription = self.get_texture(
            [res for res in self.controller.GetResources() if "RPDepth" in res.name][0].resourceId)

        self.check(draw is not None)

        self.controller.SetFrameEvent(draw.next.eventId, True)

        # At the start they should be cleared

        for y in range(0, rpcol.height-1, 17):
            for x in range(0, rpcol.width-1, 17):
                self.check_pixel_value(rpcol.resourceId, x, y, [0.0, 1.0, 0.0, 1.0])
                self.check_pixel_value(rpdepth.resourceId, x, y, [0.4, float(0x40)/float(255), 0.0, 1.0])

        rdtest.log.success("Values are correct before the renderpass")

        draw = self.find_draw("TestMiddle")

        self.controller.SetFrameEvent(draw.next.eventId, True)

        for y in range(0, rpcol.height-1, 17):
            for x in range(0, rpcol.width-1, 17):

                # if we're in the rect, check for pattern colors
                if 50 <= x < 125 and 50 <= y < 125:
                    c: rd.PixelValue = self.controller.PickPixel(rpcol.resourceId, x, y, rd.Subresource(),
                                                                 rd.CompType.Typeless)
                    d: rd.PixelValue = self.controller.PickPixel(rpdepth.resourceId, x, y, rd.Subresource(),
                                                                 rd.CompType.Typeless)

                    if not rdtest.value_compare(c.floatValue, [0.0] * 4) and not rdtest.value_compare(c.floatValue,
                                                                                                      [1000.0] * 4):
                        raise rdtest.TestFailureException(
                            'middle color has unexpected value at {},{}: {}'.format(x, y, c.floatValue))

                    if not rdtest.value_compare(d.floatValue[0:2], [0.0] * 2) and not rdtest.value_compare(
                            d.floatValue[0:2], [1.0] * 2):
                        raise rdtest.TestFailureException(
                            'middle depth has unexpected value at {},{}: {}'.format(x, y, d.floatValue))
                else:
                    self.check_pixel_value(rpcol.resourceId, x, y, [0.0, 1.0, 0.0, 1.0])
                    self.check_pixel_value(rpdepth.resourceId, x, y, [0.4, float(0x40)/float(255), 0.0, 1.0])

        middle_col_bytes = self.controller.GetTextureData(rpcol.resourceId, rd.Subresource())
        middle_depth_bytes = self.controller.GetTextureData(rpdepth.resourceId, rd.Subresource())

        rdtest.log.success("Values are correct in the middle of the renderpass")

        draw = self.find_draw("TestEnd")

        self.controller.SetFrameEvent(draw.next.eventId, True)

        for y in range(0, rpcol.height-1, 17):
            for x in range(0, rpcol.width-1, 17):

                # if we're in the rect, check for pattern colors
                if 50 <= x < 125 and 50 <= y < 125:
                    c: rd.PixelValue = self.controller.PickPixel(rpcol.resourceId, x, y, rd.Subresource(),
                                                                 rd.CompType.Typeless)
                    d: rd.PixelValue = self.controller.PickPixel(rpdepth.resourceId, x, y, rd.Subresource(),
                                                                 rd.CompType.Typeless)

                    if not rdtest.value_compare(c.floatValue, [0.0] * 4) and not rdtest.value_compare(c.floatValue,
                                                                                                      [1000.0] * 4):
                        raise rdtest.TestFailureException(
                            'middle color has unexpected value at {},{}: {}'.format(x, y, c.floatValue))

                    if not rdtest.value_compare(d.floatValue[0:2], [0.0] * 2) and not rdtest.value_compare(
                            d.floatValue[0:2], [1.0] * 2):
                        raise rdtest.TestFailureException(
                            'middle depth has unexpected value at {},{}: {}'.format(x, y, d.floatValue))
                else:
                    self.check_pixel_value(rpcol.resourceId, x, y, [0.0, 1.0, 0.0, 1.0])
                    self.check_pixel_value(rpdepth.resourceId, x, y, [0.4, float(0x40)/float(255), 0.0, 1.0])

        rdtest.log.success("Values are correct after the renderpass")

        end_col_bytes = self.controller.GetTextureData(rpcol.resourceId, rd.Subresource())
        end_depth_bytes = self.controller.GetTextureData(rpdepth.resourceId, rd.Subresource())

        self.check(middle_col_bytes != end_col_bytes)
        self.check(middle_depth_bytes != end_depth_bytes)

        draw = self.find_draw("UndefinedLoad_Before")

        self.controller.SetFrameEvent(draw.next.eventId, True)

        # check that they are cleared again
        for y in range(0, rpcol.height-1, 17):
            for x in range(0, rpcol.width-1, 17):
                self.check_pixel_value(rpcol.resourceId, x, y, [0.0, 1.0, 0.0, 1.0])
                self.check_pixel_value(rpdepth.resourceId, x, y, [0.4, float(0x40)/float(255), 0.0, 1.0])

        rdtest.log.success("Values are correct before the UNDEFINED initial layout renderpass")

        draw = self.find_draw("UndefinedLoad_After")

        self.controller.SetFrameEvent(draw.next.eventId, True)

        # check that they are all undefined pattern - initial layout affects the whole resource
        for y in range(0, rpcol.height-1, 17):
            for x in range(0, rpcol.width-1, 17):
                c: rd.PixelValue = self.controller.PickPixel(rpcol.resourceId, x, y, rd.Subresource(),
                                                             rd.CompType.Typeless)
                d: rd.PixelValue = self.controller.PickPixel(rpdepth.resourceId, x, y, rd.Subresource(),
                                                             rd.CompType.Typeless)

                if not rdtest.value_compare(c.floatValue, [0.0] * 4) and not rdtest.value_compare(c.floatValue,
                                                                                                  [1000.0] * 4):
                    raise rdtest.TestFailureException(
                        'undefined color has unexpected value at {},{}: {}'.format(x, y, c.floatValue))

                if not rdtest.value_compare(d.floatValue[0:2], [0.0] * 2) and not rdtest.value_compare(
                        d.floatValue[0:2], [1.0] * 2):
                    raise rdtest.TestFailureException(
                        'undefined depth has unexpected value at {},{}: {}'.format(x, y, d.floatValue))

        rdtest.log.success("Values are correct after the UNDEFINED initial layout renderpass")
