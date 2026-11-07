package mcdiamond.mixin;

import java.util.function.Consumer;
import net.minecraft.class_1297;
import net.minecraft.class_2596;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;
import org.spongepowered.asm.mixin.gen.Invoker;

@Mixin(targets = "net.minecraft.class_3231", remap = false)
public interface TickStateAccess {
    @Accessor(value = "field_14049", remap = false)
    class_1297 mcdiamondEntity();

    @Accessor(value = "field_18259", remap = false)
    Consumer<class_2596<?>> mcdiamondWatchers();

    @Invoker(value = "method_18761", remap = false)
    void mcdiamondPositionBaseline();

    @Invoker(value = "method_14306", remap = false)
    void mcdiamondFlushData();
}
