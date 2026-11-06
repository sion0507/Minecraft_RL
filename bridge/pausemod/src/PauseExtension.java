package mcdiamond;

import carpet.CarpetExtension;
import carpet.CarpetServer;
import carpet.helpers.TickSpeed;
import net.fabricmc.api.ModInitializer;
import net.minecraft.server.MinecraftServer;
import net.minecraft.class_2170;
import net.minecraft.class_2540;
import net.minecraft.class_2658;
import net.minecraft.class_2960;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import io.netty.buffer.Unpooled;
import java.nio.charset.StandardCharsets;

/** Own extension: load snapshots without advancing them before the first request. */
public final class PauseExtension implements ModInitializer, CarpetExtension {
    private static String pending;
    private static long before;
    private static int ticks;

    @Override
    public void registerCommands(CommandDispatcher<net.minecraft.class_2168> dispatcher) {
        dispatcher.register(class_2170.method_9247("mcdiamond_step")
            .requires(source -> source.method_9259(4) && source.method_9228() == null)
            .then(class_2170.method_9244("ticks", IntegerArgumentType.integer(1, 400))
            .then(class_2170.method_9244("nonce", StringArgumentType.word()).executes(context -> {
                String nonce = StringArgumentType.getString(context, "nonce");
                if (pending != null || !TickSpeed.deeplyFrozen() ||
                    !nonce.matches("[0-9a-f-]{36}")) return 0;
                before = context.getSource().method_9211().method_30002().method_8510();
                ticks = IntegerArgumentType.getInteger(context, "ticks");
                pending = nonce;
                TickSpeed.add_ticks_to_run_in_pause(ticks);
                return 1;
            }))));
    }

    public static void completedTick(MinecraftServer server) {
        if (pending == null) return;
        long after = server.method_30002().method_8510();
        if (after - before < ticks) return;
        byte[] receipt = (pending + " " + before + " " + after).getBytes(StandardCharsets.UTF_8);
        pending = null;
        // FIFO delivery makes all preceding block/entity/inventory updates visible first.
        for (net.minecraft.class_3222 player : server.method_3760().method_14571()) {
            player.field_13987.method_14364(new class_2658(new class_2960("mcdiamond:tick"),
                new class_2540(Unpooled.wrappedBuffer(receipt))));
        }
    }

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
