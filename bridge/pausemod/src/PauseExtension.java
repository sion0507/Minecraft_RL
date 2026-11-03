package mcdiamond;

import carpet.CarpetExtension;
import carpet.CarpetServer;
import carpet.helpers.TickSpeed;
import net.fabricmc.api.ModInitializer;
import net.minecraft.server.MinecraftServer;

/** Own extension: load snapshots without advancing them before the first request. */
public final class PauseExtension implements ModInitializer, CarpetExtension {
    @Override
    public void onInitialize() {
        CarpetServer.manageExtension(this);
    }

    @Override
    public void onServerLoaded(MinecraftServer server) {
        TickSpeed.setFrozenState(true, true);
    }

    @Override
    public void onPlayerLoggedIn(net.minecraft.class_3222 player) {
        // A frozen player still needs the initial status packet to complete client spawn.
        CarpetServer.minecraft_server.method_3760().method_14594(player);
        player.field_13987.method_14364(new net.minecraft.class_2749(
            player.method_6032(), player.method_7344().method_7586(), player.method_7344().method_7589()));
        player.field_13987.method_14364(new net.minecraft.class_2739(
            player.method_5628(), player.method_5841(), true));
    }
}
